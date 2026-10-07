"""Waste Recovery Score & Route Selection Engine."""
import json
import os
from dataclasses import dataclass, field
import yaml

ROUTES = ["reuse", "recycle", "compost", "material_recovery", "authorized_ewaste_collection", "safe_disposal"]

# Primary category to material baseline
CATEGORY_TO_MATERIAL = {
    "Cardboard": "Cellulose / Corrugated Fibreboard",
    "Food Organics": "Organic Biodegradable Matter",
    "Glass": "Silica Soda-Lime Glass",
    "Metal": "Aluminium / Ferrous Metal",
    "Miscellaneous Trash": "Composite / Non-recyclable Waste",
    "Paper": "Cellulose Wood Fibre",
    "Plastic": "Polymer (PET/HDPE/PP/LDPE)",
    "Textile Trash": "Natural / Synthetic Fibre",
    "Vegetation": "Lignocellulosic Green Biomass"
}

BASE_MATERIAL_SCORES = {
    "Cardboard": 88.0,
    "Food Organics": 80.0,
    "Glass": 92.0,
    "Metal": 95.0,
    "Miscellaneous Trash": 20.0,
    "Paper": 82.0,
    "Plastic": 75.0,
    "Textile Trash": 60.0,
    "Vegetation": 85.0
}

CONDITION_MULTIPLIERS = {
    "clean": 1.0,
    "dry": 1.0,
    "intact": 1.0,
    "damp": 0.85,
    "dirty": 0.70,
    "greasy": 0.50,
    "heavily_soiled": 0.35,
    "contaminated": 0.25,
    "damaged": 0.80,
    "unknown": 0.85,
    None: 0.85
}

CATEGORY_ROUTES = {
    "Cardboard": ("recycle", ["recycle", "reuse"]),
    "Food Organics": ("compost", ["compost"]),
    "Glass": ("recycle", ["recycle", "reuse"]),
    "Metal": ("recycle", ["recycle", "material_recovery"]),
    "Miscellaneous Trash": ("safe_disposal", ["safe_disposal"]),
    "Paper": ("recycle", ["recycle"]),
    "Plastic": ("recycle", ["recycle", "material_recovery"]),
    "Textile Trash": ("material_recovery", ["reuse", "material_recovery", "safe_disposal"]),
    "Vegetation": ("compost", ["compost"])
}

RECYCLING_PROFILES = {
    "Cardboard": {
        "recyclability_index": 88.0,
        "grade_label": "Grade A - Industrial Corrugated Fibreboard",
        "market_scrap_rate": "Rs. 11 - 15 / kg",
        "energy_savings_pct": 74.0,
        "co2_reduction_kg_per_kg": 1.4,
        "water_savings_liters_per_kg": 26.0,
        "lifecycle_loops": "5 to 7 mechanical cycles before fiber shortening",
        "downcycling_risk": "Low (Closed-loop into kraft boxes, liners, and core paper)",
        "processing_method": "Hydrapulping -> Centrifugal De-trashing -> Screen Refining -> Roll Pressing",
        "contamination_sensitivity": "High (Food grease & moisture break hydrogen bonding in cellulose)",
        "economic_viability": "Very High (Consistently high demand across paper mills in Maharashtra)",
        "buyer_industries": ["Packaging Manufacturers", "Paper & Board Mills", "E-commerce Logistics Units"]
    },
    "Plastic": {
        "recyclability_index": 76.0,
        "grade_label": "Polymer Resins (PET #1, HDPE #2, PP #5)",
        "market_scrap_rate": "Rs. 26 - 38 / kg (Clean PET/HDPE Flakes)",
        "energy_savings_pct": 88.0,
        "co2_reduction_kg_per_kg": 1.8,
        "water_savings_liters_per_kg": 12.0,
        "lifecycle_loops": "2 to 3 mechanical cycles; infinite via chemical depolymerization",
        "downcycling_risk": "Moderate (Downcycles into polyester staple fiber, strapping tape, or composite pavers)",
        "processing_method": "Optical NIR Sorting -> Granulation -> Hot Caustic Bath (85°C) -> Extrusion Pelletizing",
        "contamination_sensitivity": "Medium (Adhesive labels, PVC liners, and oily residues must be purged)",
        "economic_viability": "High (Strong demand driven by statutory Extended Producer Responsibility (EPR) targets)",
        "buyer_industries": ["Textile & Fleece Manufacturers", "Plastic Moulding Plants", "Road Bitumen Aggregates"]
    },
    "Metal": {
        "recyclability_index": 96.0,
        "grade_label": "Aluminium (UBC) & Non-Ferrous Alloys",
        "market_scrap_rate": "Rs. 125 - 155 / kg (Aluminium) | Rs. 28 - 35 / kg (Steel)",
        "energy_savings_pct": 95.0,
        "co2_reduction_kg_per_kg": 9.2,
        "water_savings_liters_per_kg": 40.0,
        "lifecycle_loops": "Infinite closed-loop (Zero atomic degradation or property loss during remelting)",
        "downcycling_risk": "Negligible (100% true circularity; can-to-can closed loop)",
        "processing_method": "Magnetic & Eddy Current Separation -> Shredding -> De-lacquering -> Induction Smelting into Ingots",
        "contamination_sensitivity": "Low (Organic and paint coatings burn off cleanly in 660°C smelting furnace)",
        "economic_viability": "Extremely High (Highest commercial value scrap commodity in Indian secondary markets)",
        "buyer_industries": ["Aluminium Smelters", "Automobile Foundry Castings", "Beverage Can Manufacturers"]
    },
    "Glass": {
        "recyclability_index": 92.0,
        "grade_label": "Container Soda-Lime Cullet Glass",
        "market_scrap_rate": "Rs. 3.5 - 6.0 / kg (Sorted Clean Cullet)",
        "energy_savings_pct": 30.0,
        "co2_reduction_kg_per_kg": 0.6,
        "water_savings_liters_per_kg": 8.0,
        "lifecycle_loops": "Infinite closed-loop (Zero chemical loss or molecular breakdown)",
        "downcycling_risk": "Negligible if color-sorted (Clear Flint, Amber, Emerald); aggregate filler if mixed",
        "processing_method": "Optical Color Sorting -> Crushing into Cullet -> De-metallization -> Furnace Melting at 1500°C",
        "contamination_sensitivity": "Medium (Ceramics, stones, and heat-resistant Pyrex ruin furnace melt)",
        "economic_viability": "High (Breweries, pharmaceutical vial bottlers, and food jars)",
        "buyer_industries": ["Glass Bottling Plants", "Fiberglass Insulation Units", "Construction Aggregates"]
    },
    "Food Organics": {
        "recyclability_index": 85.0,
        "grade_label": "Organic Biodegradable Biomass",
        "market_scrap_rate": "Rs. 4.0 - 7.0 / kg (Finished Enriched Compost / CBG Equivalent)",
        "energy_savings_pct": 65.0,
        "co2_reduction_kg_per_kg": 0.8,
        "water_savings_liters_per_kg": 15.0,
        "lifecycle_loops": "Ecological biological nutrient replenishment (Returns N, P, K to topsoil)",
        "downcycling_risk": "None (High-value biological conversion into Bio-CNG / Compressed Bio-Gas or organic manure)",
        "processing_method": "Anaerobic Biomethanation Digester -> Thermophilic Windrow Composting (55°C) -> Screening",
        "contamination_sensitivity": "High (Inert plastic bags, batteries, and glass fragments contaminate compost)",
        "economic_viability": "High (Mandatory municipal park usage, organic farming, and city gas grid)",
        "buyer_industries": ["Agricultural Cooperatives", "Municipal Parks", "Bio-CNG Fuel Stations"]
    },
    "Paper": {
        "recyclability_index": 82.0,
        "grade_label": "High-Grade Bleached & Mixed Cellulose Fibre",
        "market_scrap_rate": "Rs. 9.0 - 13.0 / kg",
        "energy_savings_pct": 65.0,
        "co2_reduction_kg_per_kg": 1.3,
        "water_savings_liters_per_kg": 24.0,
        "lifecycle_loops": "4 to 6 cycles before fibers become too short to bind",
        "downcycling_risk": "Moderate (Office printing paper cascades down into newsprint, tissue, and egg trays)",
        "processing_method": "Hydrapulping -> Ink Flotation De-inking -> Fiber Fractionation -> Paper Machine Drying",
        "contamination_sensitivity": "High (Food grease, wax coatings, and moisture degrade pulp quality)",
        "economic_viability": "High (High demand across industrial paper manufacturing belts)",
        "buyer_industries": ["Paper Mills", "Stationery Converters", "Cardboard Box Manufacturers"]
    },
    "Vegetation": {
        "recyclability_index": 88.0,
        "grade_label": "Green Lignocellulosic Horticultural Waste",
        "market_scrap_rate": "Rs. 3.0 - 5.0 / kg (Mulch & Biomass Briquette Pellets)",
        "energy_savings_pct": 70.0,
        "co2_reduction_kg_per_kg": 0.9,
        "water_savings_liters_per_kg": 10.0,
        "lifecycle_loops": "Nutrient replenishment & Soil carbon sequestration",
        "downcycling_risk": "None (Converted into protective horticultural mulch or green coal briquettes)",
        "processing_method": "High-Speed Wood Chipper Shredder -> Aerated Static Pile Composting / Briquetting Press",
        "contamination_sensitivity": "Low (Can tolerate trace soil; large stones and metal wires must be screened)",
        "economic_viability": "High (Substitutes coal in industrial boilers and conditions urban soils)",
        "buyer_industries": ["Industrial Boiler Operators", "Landscaping Firms", "Organic Nurseries"]
    },
    "Textile Trash": {
        "recyclability_index": 60.0,
        "grade_label": "Mixed Cotton, Polyester & Synthetic Blends",
        "market_scrap_rate": "Rs. 6.0 - 12.0 / kg",
        "energy_savings_pct": 50.0,
        "co2_reduction_kg_per_kg": 3.6,
        "water_savings_liters_per_kg": 60.0,
        "lifecycle_loops": "1 to 2 mechanical cycles (Shoddy yarn / Non-woven felt)",
        "downcycling_risk": "High (Downcycled into industrial wiping rags, acoustic insulation, or carpet underlay)",
        "processing_method": "Metal Trim Removal -> Rotary Blade Chopping -> Garnetting Fiber Pulling -> Needle Punching",
        "contamination_sensitivity": "High (Dampness, mildew, and complex multi-fiber elastane blends reduce yield)",
        "economic_viability": "Moderate (Growing textile recycling clusters across Bhiwandi, Solapur, and Surat)",
        "buyer_industries": ["Automotive Insulation", "Acoustic Panel Plants", "Industrial Wiper Suppliers"]
    },
    "Miscellaneous Trash": {
        "recyclability_index": 22.0,
        "grade_label": "Multi-Layered Plastic (MLP) & Composite Inerts",
        "market_scrap_rate": "Rs. 0.5 - 2.0 / kg (Refuse Derived Fuel (RDF) Calorific Value)",
        "energy_savings_pct": 25.0,
        "co2_reduction_kg_per_kg": 0.3,
        "water_savings_liters_per_kg": 0.0,
        "lifecycle_loops": "Single-use thermal recovery / Road polymer binding",
        "downcycling_risk": "Full downcycling (Processed into RDF pellets for co-processing in cement kilns)",
        "processing_method": "High-Torque Shredding -> Air Density Classification -> Thermal Drying -> RDF Pelletizing",
        "contamination_sensitivity": "Low for thermal co-processing; high moisture lowers Net Calorific Value (NCV)",
        "economic_viability": "Low (Relies on municipal tipping fee or EPR brand owner subsidies)",
        "buyer_industries": ["Cement Manufacturing Kilns", "Waste-to-Energy Boilers", "Bitumen Road Contractors"]
    }
}

def get_recycling_potential(waste_class: str, condition: str = None) -> dict:
    """Returns deep recycling potential metrics for the specified waste category."""
    base = RECYCLING_PROFILES.get(waste_class, RECYCLING_PROFILES["Miscellaneous Trash"]).copy()
    
    cond_factor = 1.0
    if condition:
        c_low = condition.lower()
        if "dirty" in c_low or "soiled" in c_low:
            cond_factor = 0.85
        elif "greas" in c_low or "food" in c_low:
            cond_factor = 0.65
        elif "damag" in c_low:
            cond_factor = 0.90
        elif "clean" in c_low or "dry" in c_low:
            cond_factor = 1.05

    effective_index = round(min(100.0, max(5.0, base["recyclability_index"] * cond_factor)), 1)
    base["effective_recyclability_index"] = effective_index
    base["condition_impact"] = f"Condition factor: {cond_factor:.2f}x"
    return base

@dataclass
class RecoveryInput:
    waste_class: str
    material: str | None = None
    condition: str | None = None   # Manual input or None; never fabricated

@dataclass
class RecoveryResult:
    score: float
    score_version: str
    route: str
    candidate_routes: list[str]
    detected_material: str
    condition_used: str
    factor_breakdown: dict
    statutory_guidance: dict
    rationale: str
    recycling_potential: dict = field(default_factory=dict)

def load_material_guidance() -> dict:
    guidance_path = "Project Data/Recycling/material_guidance"
    if os.path.exists(guidance_path):
        try:
            with open(guidance_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

_GUIDANCE_CACHE = None

def get_guidance():
    global _GUIDANCE_CACHE
    if _GUIDANCE_CACHE is None:
        _GUIDANCE_CACHE = load_material_guidance()
    return _GUIDANCE_CACHE

def score_recovery(inp: RecoveryInput) -> RecoveryResult:
    waste_class = inp.waste_class
    material = inp.material or CATEGORY_TO_MATERIAL.get(waste_class, "Mixed Material")
    
    guidance_data = get_guidance().get(waste_class, {})
    
    # 1. Base material recoverability (0-40 pts)
    base_raw = BASE_MATERIAL_SCORES.get(waste_class, 50.0)
    mat_score = round(base_raw * 0.40, 2)
    
    # 2. Condition factor (0-25 pts)
    cond_key = inp.condition.lower() if inp.condition else None
    mult = CONDITION_MULTIPLIERS.get(cond_key, 0.85)
    condition_display = inp.condition if inp.condition else "Condition unavailable (baseline applied)"
    cond_score = round(25.0 * mult, 2)
    
    # 3. Route feasibility (0-20 pts)
    default_route, candidates = CATEGORY_ROUTES.get(waste_class, ("safe_disposal", ["safe_disposal"]))
    feasibility_score = 18.0 if default_route in ["recycle", "compost"] else (14.0 if default_route == "reuse" else 10.0)
    
    # 4. Local handling factor (0-15 pts)
    handling_score = 12.0 if waste_class in ["Cardboard", "Paper", "Metal", "Glass", "Food Organics"] else 8.0
    
    total_score = round(mat_score + cond_score + feasibility_score + handling_score, 1)
    total_score = min(100.0, max(0.0, total_score))
    
    statutory_info = {
        "stream_type": guidance_data.get("stream_type", "Dry / Wet Segregated"),
        "recommended_bin": guidance_data.get("recommended_bin_color", "Blue/Green"),
        "statutory_pathway": guidance_data.get("statutory_pathway", "SWM Rules 2016"),
        "community_tips": guidance_data.get("community_action_tips", [])
    }
    
    rationale = (
        f"Waste Recovery Score is {total_score}/100. Best pathway is '{default_route}'. "
        f"Base material intrinsic recyclability is {mat_score}/40, condition factor is {cond_score}/25 "
        f"({condition_display}), route feasibility is {feasibility_score}/20, and handling factor is {handling_score}/15."
    )
    
    potential = get_recycling_potential(waste_class, inp.condition)

    return RecoveryResult(
        score=total_score,
        score_version="1.0.0-verified",
        route=default_route,
        candidate_routes=candidates,
        detected_material=material,
        condition_used=condition_display,
        factor_breakdown={
            "material_factor": mat_score,
            "condition_factor": cond_score,
            "route_feasibility_factor": feasibility_score,
            "local_handling_factor": handling_score
        },
        statutory_guidance=statutory_info,
        rationale=rationale,
        recycling_potential=potential
    )
