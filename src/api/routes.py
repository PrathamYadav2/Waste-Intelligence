"""FastAPI route implementations connecting real models, database, and analytics."""
import os
import io
import json
import base64
from datetime import datetime, timezone
from typing import Optional
from PIL import Image

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query
from fastapi.responses import JSONResponse

from .auth import require_user
from .schemas import (
    HealthResponse, ClassifyResponse, ClassScore,
    RecoveryRequest, RecoveryResponse, RecommendationItem
)
from ..config import get_settings
from ..vision.classifier import ClassifierFactory, ImageClassifier
from ..explainability.gradcam import explain
from ..recovery.scoring import RecoveryInput, score_recovery
from ..recommendations.engine import recommend
from ..database.session import get_session
from ..vision.registry import list_models
import pandas as pd
from sqlalchemy import text

health_router = APIRouter()
router = APIRouter(dependencies=[Depends(require_user)])

# Cached classifier instance
_CLASSIFIER: Optional[ImageClassifier] = None

def get_classifier() -> ImageClassifier:
    global _CLASSIFIER
    if _CLASSIFIER is None:
        model_path = "models/image_classifier/realwaste_mobilenet_v3.pth"
        if not os.path.exists(model_path):
            raise RuntimeError("Model not trained")
        _CLASSIFIER = ClassifierFactory.create("mobilenet_v3_small")
        _CLASSIFIER.load(model_path)
    return _CLASSIFIER


@health_router.get("/health", response_model=HealthResponse)
async def health():
    model_status = "LOADED" if os.path.exists("models/image_classifier/realwaste_mobilenet_v3.pth") else "NOT_TRAINED"
    db_status = "CONNECTED" if os.path.exists("waste_intelligence.db") else "NOT_INITIALIZED"
    forecast_status = "READY" if os.path.exists("data/processed/forecasts_2024_2027.csv") else "NOT_GENERATED"
    
    return HealthResponse(
        status="ok",
        version="1.0.0",
        time=datetime.now(timezone.utc),
        components={
            "image_classifier": model_status,
            "database": db_status,
            "forecasting": forecast_status,
            "regional_data": "CONNECTED"
        }
    )


@router.post("/waste/classify")
async def classify(image: UploadFile = File(...)):
    try:
        clf = get_classifier()
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": {"code": "MODEL_UNAVAILABLE", "message": "Model not trained"}})

    contents = await image.read()
    try:
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        return JSONResponse(status_code=400, content={"error": {"code": "INVALID_IMAGE", "message": "Cannot parse uploaded image."}})

    pred = clf.predict(pil_img)
    
    # Material lookup
    rec_res = score_recovery(RecoveryInput(waste_class=pred.label))

    return {
        "request_id": f"req_{int(datetime.now().timestamp()*1000)}",
        "model_version": getattr(clf, "version", "1.0.0"),
        "prediction": {"label": pred.label, "confidence": round(pred.confidence, 4)},
        "top_k": [{"label": l, "confidence": round(c, 4)} for l, c in pred.top_k],
        "material": rec_res.detected_material
    }


@router.post("/waste/analyze")
async def analyze(
    image: UploadFile = File(...),
    region: Optional[str] = Form(None),
    condition: Optional[str] = Form(None)
):
    try:
        clf = get_classifier()
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": {"code": "MODEL_UNAVAILABLE", "message": "Model not trained"}})

    contents = await image.read()
    try:
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        return JSONResponse(status_code=400, content={"error": {"code": "INVALID_IMAGE", "message": "Cannot parse uploaded image."}})

    # 1. Classification
    pred = clf.predict(pil_img)

    # 2. Grad-CAM
    heatmap, overlay = explain(clf, pil_img)
    overlay_pil = Image.fromarray(overlay)
    buffered = io.BytesIO()
    overlay_pil.save(buffered, format="JPEG")
    gradcam_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 3. Recovery scoring
    rec_input = RecoveryInput(waste_class=pred.label, condition=condition)
    rec_res = score_recovery(rec_input)

    # 4. Regional pressure if region is specified
    db = get_session()
    pressure_info = None
    capacity_gap_val = None
    if region:
        row = db.execute(text("SELECT pressure_index, category, untreated_gap_tpd FROM capacity_analysis WHERE region = :reg"), {"reg": region}).fetchone()
        if row:
            pressure_info = {"pressure_index": float(row[0]), "category": str(row[1])}
            capacity_gap_val = float(row[2]) if row[2] is not None else None

    # 5. Recommendation
    reco = recommend(
        classification_label=pred.label,
        confidence=pred.confidence,
        recovery=rec_res,
        regional_pressure=pressure_info,
        capacity_gap=capacity_gap_val
    )

    # 6. Database log
    try:
        cur_time = datetime.now(timezone.utc).isoformat()
        db.execute(text("""
            INSERT INTO waste_observations (image_uri, region, user_condition_input, observed_at)
            VALUES (:uri, :reg, :cond, :time)
        """), {"uri": image.filename or "upload.jpg", "reg": region, "cond": condition, "time": cur_time})
        obs_id = db.execute(text("SELECT last_insert_rowid()")).scalar()

        db.execute(text("""
            INSERT INTO recommendations (observation_id, region, recommended_action, priority, explanation, route, community_action, component_trace)
            VALUES (:obs_id, :reg, :action, :prio, :expl, :route, :comm, :trace)
        """), {
            "obs_id": obs_id, "reg": region, "action": reco.action, "prio": reco.priority,
            "expl": reco.explanation, "route": reco.route, "comm": reco.community_action,
            "trace": json.dumps(reco.component_trace)
        })
        db.commit()
    except Exception as db_err:
        db.rollback()
    finally:
        db.close()

    return {
        "classification": {
            "label": pred.label,
            "confidence": round(pred.confidence, 4),
            "top_k": [{"label": l, "confidence": round(c, 4)} for l, c in pred.top_k]
        },
        "recovery": {
            "score": rec_res.score,
            "score_version": rec_res.score_version,
            "route": rec_res.route,
            "candidate_routes": rec_res.candidate_routes,
            "material": rec_res.detected_material,
            "condition": rec_res.condition_used,
            "factor_breakdown": rec_res.factor_breakdown,
            "statutory_guidance": rec_res.statutory_guidance,
            "rationale": rec_res.rationale
        },
        "recommendation": {
            "action": reco.action,
            "route": reco.route,
            "priority": reco.priority,
            "explanation": reco.explanation,
            "citizen_protocol": reco.citizen_protocol,
            "mrf_facility_action": reco.mrf_facility_action,
            "circular_economy_demand": reco.circular_economy_demand,
            "environmental_impact": reco.environmental_impact,
            "community_action": reco.community_action,
            "component_trace": reco.component_trace
        },
        "recycling_potential": reco.recycling_potential or getattr(rec_res, "recycling_potential", {}),
        "explainability": {
            "method": "Grad-CAM",
            "overlay_base64": f"data:image/jpeg;base64,{gradcam_b64}",
            "disclaimer": "Highlighted regions indicate image areas that contributed to the model prediction. They do not guarantee that the prediction is correct."
        }
    }


@router.get("/recommendations/simulate")
async def simulate_recommendation(
    waste_class: str = Query("Cardboard"),
    condition: Optional[str] = Query(None),
    weight_kg: float = Query(1.0)
):
    rec_input = RecoveryInput(waste_class=waste_class, condition=condition)
    rec_res = score_recovery(rec_input)
    reco = recommend(
        classification_label=waste_class,
        confidence=0.95,
        recovery=rec_res
    )
    scaled_impact = reco.environmental_impact.copy()
    if "co2_reduction_kg" in scaled_impact:
        scaled_impact["total_co2_avoided_kg"] = round(scaled_impact["co2_reduction_kg"] * weight_kg, 2)
    if "water_saved_liters" in scaled_impact:
        scaled_impact["total_water_saved_liters"] = round(scaled_impact["water_saved_liters"] * weight_kg, 1)

    return {
        "waste_class": waste_class,
        "weight_kg": weight_kg,
        "condition": condition,
        "recommendation": {
            "action": reco.action,
            "route": reco.route,
            "priority": reco.priority,
            "explanation": reco.explanation,
            "citizen_protocol": reco.citizen_protocol,
            "mrf_facility_action": reco.mrf_facility_action,
            "circular_economy_demand": reco.circular_economy_demand,
            "environmental_impact": scaled_impact,
            "community_action": reco.community_action,
            "component_trace": reco.component_trace
        },
        "recycling_potential": reco.recycling_potential or getattr(rec_res, "recycling_potential", {}),
        "recovery": {
            "score": rec_res.score,
            "route": rec_res.route,
            "material": rec_res.detected_material,
            "factor_breakdown": rec_res.factor_breakdown
        }
    }


@router.post("/recovery/recommend", response_model=RecoveryResponse)
async def recovery(body: RecoveryRequest):
    rec_res = score_recovery(RecoveryInput(waste_class=body.waste_class, material=body.material, condition=body.condition))
    return RecoveryResponse(
        score=rec_res.score,
        score_version=rec_res.score_version,
        route=rec_res.route,
        factor_breakdown=rec_res.factor_breakdown,
        explanation=rec_res.rationale
    )



@router.get("/regional/overview")
async def regional_overview():
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT r.region, r.year, r.gen_total_ulb_tpd, r.treated_total_ulb_tpd, r.untreated_gap_tpd, c.pressure_index, c.category, c.priority_rank
            FROM regional_waste_data r
            JOIN capacity_analysis c ON r.region = c.region
            WHERE r.year = 2023
            ORDER BY c.priority_rank ASC
        """)).fetchall()
        
        overview = []
        for r in rows:
            overview.append({
                "region": r[0],
                "year": r[1],
                "generation_tpd": float(r[2]),
                "treated_tpd": float(r[3]) if r[3] is not None else None,
                "untreated_gap_tpd": float(r[4]) if r[4] is not None else None,
                "pressure_index": float(r[5]),
                "pressure_category": r[6],
                "priority_rank": r[7]
            })
        return {"total_regions": len(overview), "regions": overview}
    finally:
        db.close()


@router.get("/regional/{region}")
async def regional_detail(region: str):
    db = get_session()
    try:
        hist_rows = db.execute(text("""
            SELECT year, gen_total_ulb_tpd, treated_total_ulb_tpd, untreated_gap_tpd, source_report
            FROM regional_waste_data
            WHERE region = :reg
            ORDER BY year ASC
        """), {"reg": region}).fetchall()

        if not hist_rows:
            return JSONResponse(status_code=404, content={"error": {"code": "NOT_FOUND", "message": f"Region '{region}' not found"}})

        fc_rows = db.execute(text("""
            SELECT target_year, predicted_tpd, lower_tpd, upper_tpd, model_name
            FROM forecasts
            WHERE region = :reg
            ORDER BY target_year ASC
        """), {"reg": region}).fetchall()

        cap_row = db.execute(text("""
            SELECT pressure_index, category, priority_rank, latest_generation_tpd, untreated_gap_tpd
            FROM capacity_analysis
            WHERE region = :reg
        """), {"reg": region}).fetchone()

        history = [{
            "year": r[0], "generation_tpd": float(r[1]),
            "treated_tpd": float(r[2]) if r[2] is not None else None,
            "untreated_gap_tpd": float(r[3]) if r[3] is not None else None,
            "source": r[4]
        } for r in hist_rows]

        forecasts = [{
            "year": r[0], "predicted_tpd": float(r[1]),
            "lower_bound": float(r[2]) if r[2] is not None else None,
            "upper_bound": float(r[3]) if r[3] is not None else None,
            "model_name": r[4]
        } for r in fc_rows]

        return {
            "region": region,
            "history": history,
            "forecasts": forecasts,
            "pressure": {
                "pressure_index": float(cap_row[0]) if cap_row else None,
                "category": cap_row[1] if cap_row else None,
                "priority_rank": cap_row[2] if cap_row else None
            }
        }
    finally:
        db.close()


@router.get("/forecast")
async def forecast_endpoint(region: Optional[str] = None):
    db = get_session()
    try:
        query = "SELECT region, target_year, predicted_tpd, lower_tpd, upper_tpd, model_name FROM forecasts"
        params = {}
        if region:
            query += " WHERE region = :reg"
            params["reg"] = region
        query += " ORDER BY region, target_year"

        rows = db.execute(text(query), params).fetchall()
        if not rows:
            return JSONResponse(status_code=404, content={"error": {"code": "NOT_FOUND", "message": "Forecast not available"}})

        res = []
        for r in rows:
            res.append({
                "region": r[0],
                "forecast_year": r[1],
                "predicted_gen_total_ulb_tpd": float(r[2]),
                "lower_bound": float(r[3]) if r[3] is not None else None,
                "upper_bound": float(r[4]) if r[4] is not None else None,
                "model_name": r[5]
            })
        return {"forecasts": res}
    finally:
        db.close()


@router.get("/map")
async def map_layer(layer: str = "generation"):
    db = get_session()
    try:
        rows = db.execute(text("""
            SELECT r.region, r.latitude, r.longitude, r.gen_total_ulb_tpd, c.pressure_index, c.category, c.priority_rank,
                   (SELECT predicted_tpd FROM forecasts WHERE region = r.region AND target_year = 2024) as fc_2024
            FROM regional_waste_data r
            JOIN capacity_analysis c ON r.region = c.region
            WHERE r.year = 2023
            ORDER BY c.priority_rank ASC
        """)).fetchall()

        features = []
        for r in rows:
            features.append({
                "region": r[0],
                "latitude": float(r[1]),
                "longitude": float(r[2]),
                "current_generation_tpd": float(r[3]),
                "pressure_index": float(r[4]),
                "pressure_category": r[5],
                "priority_rank": r[6],
                "forecast_2024_tpd": float(r[7]) if r[7] is not None else None
            })
        return {"total_features": len(features), "features": features}
    finally:
        db.close()


@router.get("/recommendations")
async def recommendations_endpoint(region: Optional[str] = None, priority: Optional[str] = None, page: int = 1, page_size: int = 20):
    db = get_session()
    try:
        query = "SELECT recommendation_id, region, recommended_action, priority, explanation, route, community_action, component_trace FROM recommendations WHERE 1=1"
        params = {}
        if region:
            query += " AND region = :reg"
            params["reg"] = region
        if priority:
            query += " AND priority = :prio"
            params["prio"] = priority
        query += " ORDER BY recommendation_id DESC LIMIT :limit OFFSET :offset"
        params["limit"] = page_size
        params["offset"] = (page - 1) * page_size

        rows = db.execute(text(query), params).fetchall()
        recos = []
        for r in rows:
            recos.append({
                "recommendation_id": r[0],
                "region": r[1],
                "action": r[2],
                "priority": r[3],
                "explanation": r[4],
                "route": r[5],
                "community_action": r[6],
                "component_trace": json.loads(r[7]) if r[7] else []
            })
        return {"items": recos, "page": page, "page_size": page_size}
    finally:
        db.close()


@router.get("/models")
async def models_endpoint():
    models_list = list_models()
    return {"models": models_list}
