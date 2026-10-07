"""Regional capacity gap and pressure index calculation."""
import numpy as np
import pandas as pd

def capacity_gap(forecast_val: float, available_capacity: float | None) -> float | None:
    """
    Formula: capacity_gap = forecast_generation - available_capacity
    If available_capacity is None or unavailable, returns None.
    """
    if available_capacity is None:
        return None
    return float(round(forecast_val - available_capacity, 2))

def compute_regional_pressure_index(current_gen: float, cagr_pct: float, treated_share_pct: float | None, gap_tpd: float | None) -> dict:
    """
    Project-Specific Analytical Index: Regional Waste Pressure Score (0-100).
    Not an official government/regulatory metric.
    Factors:
    - Generation scale factor (0-30 pts)
    - Growth rate factor (0-25 pts)
    - Untreated share / gap factor (0-30 pts)
    - Processing vulnerability factor (0-15 pts)
    """
    # 1. Scale factor: Normalized relative to 10,000 TPD max
    scale_score = min(30.0, (current_gen / 8000.0) * 30.0)
    
    # 2. Growth factor: Normalized from -5% to +20% CAGR
    growth_score = min(25.0, max(0.0, (cagr_pct + 5.0) / 25.0 * 25.0))
    
    # 3. Untreated share factor: (100 - treated_share_pct)
    if treated_share_pct is not None:
        untreated_pct = max(0.0, 100.0 - treated_share_pct)
        untreated_score = min(30.0, (untreated_pct / 100.0) * 30.0)
    else:
        untreated_score = 15.0 # default neutral
        
    # 4. Absolute gap scale factor: gap relative to 1500 TPD
    if gap_tpd is not None and gap_tpd > 0:
        gap_score = min(15.0, (gap_tpd / 1500.0) * 15.0)
    else:
        gap_score = 5.0
        
    total_index = round(scale_score + growth_score + untreated_score + gap_score, 1)
    total_index = min(100.0, max(0.0, total_index))
    
    category = "High" if total_index >= 70.0 else ("Medium" if total_index >= 45.0 else "Low")
    
    return {
        "pressure_index": total_index,
        "category": category,
        "breakdown": {
            "scale_factor": round(scale_score, 1),
            "growth_factor": round(growth_score, 1),
            "untreated_factor": round(untreated_score, 1),
            "gap_factor": round(gap_score, 1)
        },
        "explainable_summary": f"Regional pressure is {category} ({total_index}/100) driven by scale ({scale_score:.1f}/30), growth ({growth_score:.1f}/25), untreated share ({untreated_score:.1f}/30), and gap ({gap_score:.1f}/15)."
    }

def analyze_all_regions(df: pd.DataFrame) -> dict:
    results = {}
    for reg, grp in df.groupby("region"):
        grp = grp.sort_values("year")
        first_gen = grp.iloc[0]["gen_total_ulb_tpd"]
        last_gen = grp.iloc[-1]["gen_total_ulb_tpd"]
        years_span = grp.iloc[-1]["year"] - grp.iloc[0]["year"]
        cagr = ((last_gen / first_gen) ** (1 / max(1, years_span)) - 1) * 100
        
        last_treated = grp.iloc[-1].get("treated_total_ulb_tpd")
        last_share = grp.iloc[-1].get("treated_share_pct")
        last_gap = grp.iloc[-1].get("untreated_gap_tpd")
        
        treated_val = float(last_treated) if pd.notnull(last_treated) else None
        share_val = float(last_share) if pd.notnull(last_share) else None
        gap_val = float(last_gap) if pd.notnull(last_gap) else None
        
        pressure = compute_regional_pressure_index(last_gen, cagr, share_val, gap_val)
        
        results[reg] = {
            "region": reg,
            "anchor_place": grp.iloc[-1]["anchor_place"],
            "latitude": float(grp.iloc[-1]["latitude"]),
            "longitude": float(grp.iloc[-1]["longitude"]),
            "latest_year": int(grp.iloc[-1]["year"]),
            "latest_generation_tpd": float(last_gen),
            "historical_cagr_pct": round(float(cagr), 2),
            "latest_treated_tpd": treated_val,
            "latest_treated_share_pct": round(share_val, 1) if share_val is not None else None,
            "latest_untreated_gap_tpd": round(gap_val, 1) if gap_val is not None else None,
            "pressure": pressure
        }
    return results
