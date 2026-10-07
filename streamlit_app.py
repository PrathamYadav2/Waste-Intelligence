"""
AI-Based Waste Segregation, Recycling Analytics & Regional Decision Intelligence System
Streamlit Cloud Edition (Zero Serverless Constraints, Full PyTorch & Grad-CAM Support)
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st

# Setup Root Path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.vision.classifier import ClassifierFactory
from src.explainability.gradcam import explain
from src.recovery.scoring import compute_recovery_score, get_recycling_potential
from src.recommendations.engine import recommend

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Waste Intelligence & Recycling Analytics",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Aesthetic Theme Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f766e;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-green { background: #dcfce7; color: #166534; }
    .badge-blue { background: #dbeafe; color: #1e40af; }
    .badge-amber { background: #fef3c7; color: #92400e; }
    .highlight-card {
        background: #f0fdf4;
        border-left: 5px solid #16a34a;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Model & Data Caching (Streamlit Resource Cache)
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading PyTorch MobileNetV3 Model...")
def load_classifier():
    weights_path = ROOT_DIR / "models" / "image_classifier" / "realwaste_mobilenet_v3.pth"
    if not weights_path.exists():
        st.error(f"❌ Model artifact not found at {weights_path}")
        return None
    classifier = ClassifierFactory.create("mobilenet_v3_small")
    classifier.load(str(weights_path))
    return classifier

@st.cache_data
def load_forecast_data():
    csv_path = ROOT_DIR / "data" / "processed" / "forecasts_2024_2027.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.DataFrame()

classifier = load_classifier()
forecast_df = load_forecast_data()

# -----------------------------------------------------------------------------
# Sidebar Navigation & System Stats
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/recycle-sign.png", width=70)
    st.title("Waste Intelligence")
    st.markdown("**Circular Economy & ML Decision Platform**")
    st.markdown("---")

    st.markdown("### 🖥️ Model System Specs")
    st.markdown("- **Backbone:** PyTorch MobileNetV3-Small")
    st.markdown("- **Accuracy:** **78.26%** | **F1: 79.26%**")
    st.markdown("- **Weights:** `6.24 MB` (.pth loaded)")
    st.markdown("- **Explainability:** Grad-CAM saliency")
    st.markdown("- **Forecasting:** 12 Regions (2024–2027)")
    st.markdown("---")

    st.markdown("### ⚖️ Regulatory Compliance")
    st.caption("• Solid Waste Management Rules 2016\n• Plastic Waste Management Rules 2022 (EPR)\n• CPCB Municipal SWM Guidelines")
    st.markdown("---")
    st.caption("Developed for Regional Municipal Corporations & Circular Economy Stakeholders.")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">♻️ AI Waste Segregation, Recycling Analytics & Forecasting</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Computer Vision Classifier, Explainable Grad-CAM, Deep Recyclability Assessment & Regional Municipal Projections</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Main Navigation Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📷 AI Scanner & Grad-CAM",
    "📈 Regional Forecasting (2024–2027)",
    "🧠 AI Recommendation Simulator",
    "🔄 5-Step Recycling SOP"
])

# =============================================================================
# TAB 1: AI Scanner & Grad-CAM
# =============================================================================
with tab1:
    st.subheader("📷 Computer Vision Waste Classifier & Deep Saliency")
    st.markdown("Upload any waste item photo to run real-time MobileNetV3 classification, backpropagated Grad-CAM explainability, and circular recycling valuation.")

    col_up, col_res = st.columns([1, 1.4], gap="large")

    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Waste Image (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Take or upload a photo of cardboard, plastic bottle, food waste, metal, glass, etc."
        )

        sample_btn = st.button("🖼️ Load Sample Test Image (Cardboard)")
        
        target_img = None
        if uploaded_file is not None:
            target_img = Image.open(uploaded_file)
        elif sample_btn:
            sample_path = ROOT_DIR / "Project Data" / "Image Data" / "RealWaste" / "Cardboard" / "Cardboard_1.jpg"
            if sample_path.exists():
                target_img = Image.open(sample_path)
            else:
                st.warning("Sample image not found on disk.")

        if target_img:
            st.image(target_img, caption="Target Waste Image", use_container_width=True)

    with col_res:
        if target_img and classifier:
            with st.spinner("Analyzing image features & computing Grad-CAM..."):
                # Run Vision Inference
                pred = classifier.predict(target_img)
                
                # Compute Grad-CAM
                heatmap, overlay = explain(classifier, target_img)
                
                # Compute Circular Recycling Potential
                rec = get_recycling_potential(pred.label)
                
                # Compute Recovery Score & Recommendations
                recovery = compute_recovery_score(pred.label, condition="clean")
                directives = recommend(pred.label, pred.confidence, recovery)

            # Display Classification Badge
            st.success(f"### Detected: **{pred.label}** ({pred.confidence * 100:.1f}% Confidence)")

            # Top Probabilities
            st.markdown("**Top Category Probabilities:**")
            for cat, conf in pred.top_k[:4]:
                st.progress(float(conf), text=f"{cat}: {conf*100:.1f}%")

            # Dual Visual Overlay (Grad-CAM)
            st.markdown("---")
            st.markdown("#### 🔬 Explainable AI: Grad-CAM Saliency Heatmap")
            st.caption("Visual proof of deep neural feature activations driving the classification:")
            c_cam1, c_cam2 = st.columns(2)
            with c_cam1:
                st.image(heatmap, caption="Normalized Activation Saliency", clamp=True, use_container_width=True)
            with c_cam2:
                st.image(overlay, caption="Gradient Overlay on Image", use_container_width=True)

            # Recycling & Market Valuation Panel
            st.markdown("---")
            st.markdown("#### 💰 Secondary Scrap Market & Recycling Potential")
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Recyclability Index", f"{rec.recyclability_index}%", delta=rec.feasibility)
            with kpi2:
                st.metric("Indian Scrap Rate", f"₹ {rec.market_value_inr_per_kg['min_inr']} - {rec.market_value_inr_per_kg['max_inr']} / kg")
            with kpi3:
                st.metric("Degradation Cycles", rec.lifecycle_loops)

            st.info(f"**Industrial Processing SOP:** {rec.industrial_processing_sop}")
            st.markdown(f"**Target Offtake Industries:** `{', '.join(rec.target_buyer_industries)}`")

            # Multi-Tier Recommendations
            st.markdown("---")
            st.markdown("#### 📋 Action Directives (Citizen & Facility)")
            st.markdown(f"- 🏠 **Citizen Bin Assignment:** `{directives.citizen_protocol[0] if directives.citizen_protocol else 'Assigned Container'}`")
            st.markdown(f"- 🧹 **Pre-cleaning Rule:** `{directives.citizen_protocol[1] if len(directives.citizen_protocol) > 1 else 'Keep clean & uncontaminated'}`")
            st.markdown(f"- 🏭 **MRF Facility Action:** `{directives.mrf_facility_action}`")
            st.markdown(f"- 🔄 **EPR Offtake:** `{directives.circular_economy_demand}`")
        else:
            st.info("👆 Please upload an image from the left panel or click 'Load Sample Test Image' to begin.")

# =============================================================================
# TAB 2: Regional Forecasting (2024–2027)
# =============================================================================
with tab2:
    st.subheader("📈 Maharashtra Municipal Waste Forecasting (2024–2027)")
    st.markdown("Audited annual observations (2016–2023) sourced from official CPCB / MPCB State SWM Annual Reports with trend projections to 2027.")

    if not forecast_df.empty:
        regions = sorted(forecast_df["region"].unique().tolist())
        selected_region = st.selectbox("Select Urban Local Body (ULB):", regions, index=regions.index("Pune") if "Pune" in regions else 0)

        r_df = forecast_df[forecast_df["region"] == selected_region].sort_values("target_year")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        pred_2024 = r_df[r_df["target_year"] == 2024]["predicted_tpd"].values[0]
        pred_2027 = r_df[r_df["target_year"] == 2027]["predicted_tpd"].values[0]
        diff_2027 = pred_2027 - pred_2024

        with col_m1:
            st.metric("2024 Projected Load", f"{pred_2024:,.1f} TPD")
        with col_m2:
            st.metric("2027 Projected Load", f"{pred_2027:,.1f} TPD", delta=f"{diff_2027:+,.1f} TPD")
        with col_m3:
            st.metric("Forecast Model", "Damped Linear Trend")
        with col_m4:
            st.metric("Validation Accuracy", "96.83% (3.17% MAPE)")

        # Plot Trend Chart
        chart_data = r_df.set_index("target_year")[["predicted_tpd", "lower_tpd", "upper_tpd"]]
        chart_data.columns = ["Forecasted Generation (TPD)", "Lower Bound (-1.96σ)", "Upper Bound (+1.96σ)"]
        st.line_chart(chart_data)

        # Full Ledger Table
        st.markdown("#### 📋 2024–2027 Municipal Forecast Ledger (All 12 Regions)")
        
        # Aggregate view by region for 2024 and 2027
        pivoted = forecast_df.pivot(index="region", columns="target_year", values="predicted_tpd").round(1)
        pivoted["Net Change by 2027 (TPD)"] = (pivoted[2027] - pivoted[2024]).round(1)
        pivoted["Annual Growth Rate (TPD/yr)"] = ((pivoted[2027] - pivoted[2024]) / 3).round(1)
        st.dataframe(pivoted, use_container_width=True)

# =============================================================================
# TAB 3: AI Recommendation Simulator
# =============================================================================
with tab3:
    st.subheader("🧠 Multi-Tier AI Recommendation Simulator")
    st.markdown("Simulate waste batch recovery, circular economics, and carbon offset for any waste class and weight in kilograms.")

    c_sim1, c_sim2 = st.columns(2)
    with c_sim1:
        sim_class = st.selectbox(
            "Select Waste Category:",
            ["Cardboard", "Food Organics", "Glass", "Metal", "Paper", "Plastic", "Textile Trash", "Vegetation", "Miscellaneous Trash"]
        )
        sim_weight = st.slider("Batch Weight (in Kilograms):", min_value=1.0, max_value=2000.0, value=150.0, step=5.0)
        sim_condition = st.radio("Material Physical Condition:", ["clean", "contaminated", "wet"], horizontal=True)

    # Dynamic calculation
    rec_info = get_recycling_potential(sim_class)
    avg_scrap_price = (rec_info.market_value_inr_per_kg["min_inr"] + rec_info.market_value_inr_per_kg["max_inr"]) / 2
    total_scrap_value = avg_scrap_price * sim_weight
    
    # Impact calculations
    co2_factor = {"Metal": 6.8, "Plastic": 2.1, "Cardboard": 1.4, "Paper": 1.3, "Glass": 0.5, "Textile Trash": 3.2, "Food Organics": 0.8, "Vegetation": 0.6, "Miscellaneous Trash": 0.1}.get(sim_class, 1.0)
    co2_saved = round(sim_weight * co2_factor, 1)

    with c_sim2:
        st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
        st.markdown(f"### Estimated Batch Economic Valuation: **₹ {total_scrap_value:,.2f}**")
        st.markdown(f"- **Material Feasibility:** `{rec_info.feasibility}` ({rec_info.recyclability_index}% purity)")
        st.markdown(f"- **Est. Carbon Offset ($CO_2$ Avoided):** **{co2_saved:,} kg**")
        st.markdown(f"- **Lifecycle Degradation:** `{rec_info.lifecycle_loops}`")
        st.markdown(f"- **Primary Offtaker:** `{rec_info.target_buyer_industries[0]}`")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TAB 4: 5-Step Recycling SOP
# =============================================================================
with tab4:
    st.subheader("🔄 End-to-End Circular Recycling SOP")
    st.markdown("Statutory standard operating procedure under Solid Waste Management (SWM) Rules 2016 & Plastic Waste Management (PWM) Rules 2022.")

    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        st.markdown("### Step 1")
        st.markdown("**Source Segregation**")
        st.caption("Clean at generation point. Assign to Green (Wet), Blue (Dry), or Black (Inert) bins.")
    with s2:
        st.markdown("### Step 2")
        st.markdown("**Collection & Transfer**")
        st.caption("Partitioned EV tippers prevent re-mixing. Monitored through municipal GPS tracking.")
    with s3:
        st.markdown("### Step 3")
        st.markdown("**MRF Optical Sorting**")
        st.caption("NIR sensors and magnetic separators isolate high-value polymers and alloys.")
    with s4:
        st.markdown("### Step 4")
        st.markdown("**Industrial Processing**")
        st.caption("Caustic hot washing at 85°C, granulating, extrusion, and induction smelting.")
    with s5:
        st.markdown("### Step 5")
        st.markdown("**Circular Offtake (EPR)**")
        st.caption("Direct supply to certified brand owners for PCR plastic & alloy packaging.")

st.markdown("---")
st.caption("Waste Intelligence Decision System • Python 3.12 • Streamlit Community Cloud")
