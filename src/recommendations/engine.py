"""Recommendation engine. Distinguishes ML, rules, scoring, and analytics transparently."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..recovery.scoring import RecoveryResult, get_recycling_potential

class ComponentKind(str, Enum):
    ML = "ml"
    RULE = "rule"
    SCORING = "scoring"
    ANALYTICS = "analytics"

@dataclass
class Recommendation:
    action: str
    route: str
    priority: str
    explanation: str
    community_action: str
    citizen_protocol: list[str] = field(default_factory=list)
    mrf_facility_action: str = ""
    circular_economy_demand: str = ""
    environmental_impact: dict = field(default_factory=dict)
    recycling_potential: dict = field(default_factory=dict)
    component_trace: list[dict[str, str]] = field(default_factory=list)

def recommend(
    classification_label: str,
    confidence: float,
    recovery: RecoveryResult,
    regional_pressure: dict | None = None,
    forecast_trend: str | None = None,
    capacity_gap: float | None = None
) -> Recommendation:
    """
    Produces transparent, multi-factor recommendation with explicit component trace.
    Inputs:
    - ML: Image classification label and confidence
    - Scoring: Waste Recovery Score and factors
    - Rule: Statutory route mapping from SWM Rules 2016
    - Analytics: Regional pressure score, forecast, and capacity gap
    """
    component_trace = [
        {"component": "Waste Vision Classifier (MobileNetV3)", "kind": ComponentKind.ML.value, "detail": f"Detected {classification_label} ({confidence*100:.1f}% confidence)"},
        {"component": "Waste Recovery Scoring Engine", "kind": ComponentKind.SCORING.value, "detail": f"Recovery Score {recovery.score}/100 based on material & condition"},
        {"component": "SWM Statutory Rules", "kind": ComponentKind.RULE.value, "detail": f"Routed to {recovery.route} ({recovery.statutory_guidance.get('stream_type')})"}
    ]

    pressure_cat = "Medium"
    if regional_pressure and "category" in regional_pressure:
        pressure_cat = regional_pressure["category"]
        component_trace.append({
            "component": "Regional Pressure Analysis",
            "kind": ComponentKind.ANALYTICS.value,
            "detail": f"Regional Pressure {regional_pressure.get('pressure_index')}/100 ({pressure_cat})"
        })

    if capacity_gap is not None:
        component_trace.append({
            "component": "Capacity Gap Analysis",
            "kind": ComponentKind.ANALYTICS.value,
            "detail": f"Forecast Untreated Gap: {capacity_gap:.1f} TPD"
        })

    # Deep recycling potential
    rec_pot = recovery.recycling_potential or get_recycling_potential(classification_label)

    # Detailed multi-tier AI recommendation protocols per waste stream
    if recovery.route == "recycle":
        if pressure_cat == "High":
            priority = "high"
            action = f"Immediate dry-stream segregation of {classification_label} into {recovery.statutory_guidance.get('recommended_bin', 'Blue')} bin for MRF processing."
        else:
            priority = "medium"
            action = f"Source-segregate {classification_label} and channel to authorised dry waste collection."
        comm_action = f"Organize neighborhood collection drive for recyclable {classification_label} to divert dry waste from landfill."
        
        citizen_protocol = [
            f"Pre-clean: Remove any organic/liquid residue to prevent cellulose or polymer batch contamination.",
            f"Volume Reduction: Flatten cartons / crush hollow containers to optimize storage by up to 70%.",
            f"Bin Placement: Place strictly into the Blue (Dry Recyclable) bin. Do not mix with wet organic waste."
        ]
        mrf_facility_action = f"Channel to MRF optical sorting / manual conveyor belt. Compact into high-density bales for dispatch to certified {classification_label} re-processors."
        circular_economy_demand = f"Direct demand from registered Indian recycling units. Eligible for formal Extended Producer Responsibility (EPR) recycling credits."
        environmental_impact = {
            "energy_saved_pct": rec_pot.get("energy_savings_pct", 75.0),
            "co2_reduction_kg": rec_pot.get("co2_reduction_kg_per_kg", 1.5),
            "water_saved_liters": rec_pot.get("water_savings_liters_per_kg", 20.0),
            "resource_conserved": "Fossil fuels, fresh timber, bauxite ore, and virgin polymers"
        }

    elif recovery.route == "compost":
        if pressure_cat == "High":
            priority = "high"
            action = f"Divert organic waste ({classification_label}) immediately to decentralized on-site composting or bio-methanation."
        else:
            priority = "medium"
            action = f"Segregate {classification_label} into Green wet waste bin for composting."
        comm_action = "Initiate decentralized society wet-waste composting pit to eliminate organic waste transportation."
        
        citizen_protocol = [
            "Source Segregation: Ensure zero plastic liners, tags, or staples enter the organic bin.",
            "Moisture Balance: Drain excess liquid before placing into the Green (Wet Waste) bin.",
            "Decentralized Composting: If residential society has a compost pit or bio-digester, deposit directly within 24 hours."
        ]
        mrf_facility_action = "Transfer to municipal Biomethanation / Bio-CNG plant or aerated windrow composting yard. Maintain 55°C thermophilic digestion for pathogen destruction."
        circular_economy_demand = "High demand from agricultural farmer cooperatives, peri-urban organic orchards, and municipal city gardens for nitrogen-rich compost."
        environmental_impact = {
            "energy_saved_pct": rec_pot.get("energy_savings_pct", 65.0),
            "co2_reduction_kg": rec_pot.get("co2_reduction_kg_per_kg", 0.85),
            "water_saved_liters": rec_pot.get("water_savings_liters_per_kg", 15.0),
            "resource_conserved": "Avoids anaerobic landfill methane emissions; enriches agricultural topsoil"
        }

    elif recovery.route == "reuse":
        priority = "medium"
        action = f"Inspect condition and clean {classification_label} for immediate reuse before discarding."
        comm_action = "Setup community reuse shelf / swap counter for reusable materials."
        citizen_protocol = [
            "Wash and sanitize container / item using mild soapy water.",
            "Repurpose for domestic dry storage, secondary packaging, or donation.",
            "When end-of-life is reached, transition item to the Blue recycling bin."
        ]
        mrf_facility_action = "Filter reusable glass bottles or sturdy containers into community reuse / deposit-return scheme collection."
        circular_economy_demand = "Direct local reuse loops preserve 100% of embodied manufacturing energy."
        environmental_impact = {
            "energy_saved_pct": 98.0,
            "co2_reduction_kg": 2.5,
            "water_saved_liters": 30.0,
            "resource_conserved": "Maximum lifecycle extension with zero industrial remanufacturing overhead"
        }

    elif recovery.route == "material_recovery":
        priority = "medium"
        action = f"Sort and aggregate {classification_label} for secondary material recovery or Refuse-Derived Fuel (RDF) co-processing."
        comm_action = "Coordinate with registered textile/composite recovery recyclers."
        citizen_protocol = [
            "Keep dry and unsoiled. Separate buttons, zippers, or non-fabric attachments if possible.",
            "Bag separately to avoid entanglement in mechanical sorting machinery.",
            "Hand over to authorized dry waste collectors or drop at municipal circular textile hubs."
        ]
        mrf_facility_action = "Shred and separate into synthetic vs natural fibers. Dense bales routed to acoustic insulation or cement kiln co-processing."
        circular_economy_demand = "Textile shoddy yarn plants, automotive sound-deadening insulation, and industrial cleaning rags."
        environmental_impact = {
            "energy_saved_pct": rec_pot.get("energy_savings_pct", 50.0),
            "co2_reduction_kg": rec_pot.get("co2_reduction_kg_per_kg", 3.0),
            "water_saved_liters": rec_pot.get("water_savings_liters_per_kg", 50.0),
            "resource_conserved": "Offsets primary cotton cultivation and petrochemical synthetic polymer synthesis"
        }

    else: # safe_disposal
        priority = "low" if pressure_cat != "High" else "medium"
        action = f"Deposit {classification_label} in Black bin for sanitary disposal or RDF energy co-processing."
        comm_action = "Conduct waste minimization campaign to reduce single-use composite and non-recyclable items."
        citizen_protocol = [
            "Wrap safely and place into Black / Grey bin (Non-recyclable inert domestic waste).",
            "Do not burn open in the open air (causes hazardous dioxin and furan air pollution).",
            "Substitute future purchases with reusable or biodegradable alternatives."
        ]
        mrf_facility_action = "Segregate into high-calorific Refuse-Derived Fuel (RDF) for cement kiln co-processing; inert residues sent to sanitary engineered landfill."
        circular_economy_demand = "Calorific energy substitution for coal in industrial boilers and cement kilns."
        environmental_impact = {
            "energy_saved_pct": 25.0,
            "co2_reduction_kg": 0.3,
            "water_saved_liters": 0.0,
            "resource_conserved": "Thermal energy recovery displacing coal; safe containment of unrecyclable inerts"
        }

    explanation = (
        f"AI Recommendation Engine formulated via multi-modal synthesis: "
        f"Computer Vision ({classification_label} at {confidence*100:.1f}%), "
        f"Recovery Score ({recovery.score}/100, pathway: '{recovery.route}'), "
        f"and Regional Pressure ({pressure_cat})."
    )

    return Recommendation(
        action=action,
        route=recovery.route,
        priority=priority,
        explanation=explanation,
        community_action=comm_action,
        citizen_protocol=citizen_protocol,
        mrf_facility_action=mrf_facility_action,
        circular_economy_demand=circular_economy_demand,
        environmental_impact=environmental_impact,
        recycling_potential=rec_pot,
        component_trace=component_trace
    )
