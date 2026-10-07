"""
Smart Waste AI & Regional Decision Intelligence System
Streamlit Edition - Matching the exact high-aesthetic Dark Dashboard of app/index.html
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

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
    page_title="Smart Waste AI & Regional Decision Intelligence",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Exact Dark Dashboard Theme Styling matching app/index.html
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #090d16;
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header Bar */
    .top-header {
        background: rgba(17, 24, 39, 0.95);
        border: 1px solid #243049;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .brand-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    .brand-sub {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    /* KPI Stat Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #111827;
        border: 1px solid #243049;
        border-radius: 12px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10b981, #3b82f6);
    }
    .kpi-num {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
        font-weight: 600;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #10b981;
        margin-top: 4px;
        font-weight: 600;
    }

    /* Section Cards */
    .section-box {
        background: #111827;
        border: 1px solid #243049;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-desc {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 20px;
    }

    /* Result Cards */
    .res-card {
        background: #1a2234;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-top: 14px;
    }

    /* Custom Streamlit adjustments */
    div[data-testid="stExpander"] {
        background-color: #111827 !important;
        border: 1px solid #243049 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stFileUploader"] {
        background-color: #111827;
        border: 2px dashed #3b82f6;
        border-radius: 12px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Model & Data Caching
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
        df = pd.read_csv(csv_path)
        # Normalize keys
        if "forecast_year" in df.columns:
            df["target_year"] = df["forecast_year"]
        if "predicted_gen_total_ulb_tpd" in df.columns:
            df["predicted_tpd"] = df["predicted_gen_total_ulb_tpd"]
        return df
    return pd.DataFrame()

classifier = load_classifier()
forecast_df = load_forecast_data()

# -----------------------------------------------------------------------------
# Top Navigation Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="top-header">
    <div>
        <div class="brand-title">♻️ Smart Waste AI & Regional Decision Intelligence</div>
        <div class="brand-sub">Computer Vision (MobileNetV3) • Explainable Grad-CAM • Circular Recycling Analytics • Regional Projections</div>
    </div>
    <div style="display: flex; gap: 8px;">
        <span class="pill">● LIVE INFERENCE</span>
        <span class="pill" style="color: #3b82f6; border-color: rgba(59,130,246,0.3); background: rgba(59,130,246,0.12);">12 MAHARASHTRA ULBs</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4 KPI Stat Cards
# -----------------------------------------------------------------------------
kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-num">4,752</div>
        <div class="kpi-label">Training Dataset</div>
        <div class="kpi-sub">RealWaste Curated Images</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-num">78.3%</div>
        <div class="kpi-label">Vision Accuracy</div>
        <div class="kpi-sub">79.3% Macro F1 (9 Classes)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-num">12 ULBs</div>
        <div class="kpi-label">Maharashtra Regions</div>
        <div class="kpi-sub">Audited CPCB/MPCB Data</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-num">96.8%</div>
        <div class="kpi-label">Forecast Accuracy</div>
        <div class="kpi-sub">3.17% MAPE • R² = 0.994</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Dual Circular Doughnut Charts (Treatment Efficiency & Stream Composition)
# -----------------------------------------------------------------------------
chart_c1, chart_c2 = st.columns(2)

with chart_c1:
    fig_eff = go.Figure(data=[go.Pie(
        labels=["Scientifically Treated Waste", "Untreated Landfill Gap"],
        values=[90.2, 9.8],
        hole=0.68,
        marker=dict(colors=["#10b981", "#ef4444"]),
        textinfo="percent",
        textfont=dict(size=14, color="#ffffff"),
        hoverinfo="label+percent"
    )])
    fig_eff.update_layout(
        title=dict(text="<b>Statewide Waste Treatment Efficiency</b><br><span style='font-size:12px;color:#94a3b8'>Annual Average Across 12 Urban Local Bodies</span>", font=dict(color="#f8fafc", size=15)),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        margin=dict(t=50, b=20, l=20, r=20),
        height=260,
        showlegend=True,
        legend=dict(font=dict(color="#94a3b8", size=11), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_eff, use_container_width=True)

with chart_c2:
    fig_comp = go.Figure(data=[go.Pie(
        labels=["Organic Wet Waste", "Dry Recyclable Material", "Refuse-Derived Fuel (RDF)", "Inerts & Debris"],
        values=[54.0, 27.0, 11.0, 8.0],
        hole=0.68,
        marker=dict(colors=["#059669", "#3b82f6", "#f59e0b", "#64748b"]),
        textinfo="percent",
        textfont=dict(size=14, color="#ffffff"),
        hoverinfo="label+percent"
    )])
    fig_comp.update_layout(
        title=dict(text="<b>Municipal Stream Composition</b><br><span style='font-size:12px;color:#94a3b8'>CPCB Characterization Guidelines</span>", font=dict(color="#f8fafc", size=15)),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        margin=dict(t=50, b=20, l=20, r=20),
        height=260,
        showlegend=True,
        legend=dict(font=dict(color="#94a3b8", size=11), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 1: AI Vision Classifier & Scanner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="section-box">
    <div class="section-title">📷 AI Vision Classifier & Explainable Grad-CAM</div>
    <div class="section-desc">Drop an image of waste to run deep transfer-learning inference across 9 RealWaste categories with backpropagated Grad-CAM activation heatmap.</div>
</div>
""", unsafe_allow_html=True)

col_upload, col_analysis = st.columns([1, 1.4], gap="large")

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload Waste Image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload waste photo (Cardboard, Plastic, Metal, Glass, Food Organics, etc.)"
    )
    
    b_col1, b_col2 = st.columns(2)
    sample_cardboard = b_col1.button("📦 Sample: Cardboard")
    sample_plastic = b_col2.button("🥤 Sample: Metal / Can")

    target_img = None
    if uploaded_file is not None:
        target_img = Image.open(uploaded_file)
    elif sample_cardboard:
        p = ROOT_DIR / "Project Data" / "Image Data" / "RealWaste" / "Cardboard" / "Cardboard_1.jpg"
        if p.exists(): target_img = Image.open(p)
    elif sample_plastic:
        p = ROOT_DIR / "Project Data" / "Image Data" / "RealWaste" / "Metal" / "Metal_1.jpg"
        if p.exists(): target_img = Image.open(p)

    if target_img:
        st.image(target_img, caption="Analyzed Image", use_container_width=True)

with col_analysis:
    if target_img and classifier:
        with st.spinner("Processing deep vision features & computing Grad-CAM..."):
            pred = classifier.predict(target_img)
            heatmap, overlay = explain(classifier, target_img)
            rec = get_recycling_potential(pred.label)
            recovery = compute_recovery_score(pred.label, condition="clean")
            directives = recommend(pred.label, pred.confidence, recovery)

        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;">
            <div style="font-size: 0.8rem; color: #10b981; font-weight: 700; text-transform: uppercase;">CLASSIFICATION RESULT</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff;">{pred.label} <span style="font-size: 1.1rem; color: #10b981;">({pred.confidence*100:.1f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Probabilities
        st.markdown("**Top Category Probabilities:**")
        for cat, conf in pred.top_k[:3]:
            st.progress(float(conf), text=f"{cat}: {conf*100:.1f}%")

        # Grad-CAM Side by Side
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔬 Explainable AI: Grad-CAM Activation Saliency")
        cam_col1, cam_col2 = st.columns(2)
        with cam_col1:
            st.image(heatmap, caption="Heatmap Saliency", clamp=True, use_container_width=True)
        with cam_col2:
            st.image(overlay, caption="Gradient Overlay on Image", use_container_width=True)

        # Recycling Potential Cards
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 💰 Deep Recycling Potential & Scrap Market Benchmark")
        
        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1:
            st.metric("Recyclability Index", f"{rec.get('recyclability_index', 80)}%", delta=rec.get('economic_viability', 'High'))
        with m_c2:
            st.metric("Market Scrap Rate", str(rec.get('market_scrap_rate', 'Rs. 15-25/kg')))
        with m_c3:
            st.metric("Lifecycle Loops", str(rec.get('lifecycle_loops', '5-7 cycles'))[:30])

        st.markdown(f"""
        <div class="res-card">
            <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 6px;"><b>Industrial Processing SOP:</b> {rec.get('processing_method', 'Mechanical Recycling & Refining')}</div>
            <div style="font-size: 0.85rem; color: #94a3b8;"><b>Target Buyer Industries:</b> <span style="color: #38bdf8;">{', '.join(rec.get('buyer_industries', ['Paper & Board Mills', 'Recyclers']))}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Directives
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📋 Multi-Tier Action Directives")
        st.markdown(f"- 🏠 **Citizen Bin Protocol:** `{directives.citizen_protocol[0] if directives.citizen_protocol else 'Assigned Container'}`")
        st.markdown(f"- 🧹 **Pre-cleaning Directives:** `{directives.citizen_protocol[1] if len(directives.citizen_protocol) > 1 else 'Clean & dry'}`")
        st.markdown(f"- 🏭 **MRF Facility Action:** `{directives.mrf_facility_action}`")
        st.markdown(f"- 🔄 **Circular Offtake (EPR):** `{directives.circular_economy_demand}`")
    else:
        st.info("👆 Upload an image or click a sample button on the left to run classification and Grad-CAM.")

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 2: Regional Waste Generation Forecasting (2024–2027)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="section-box">
    <div class="section-title">📈 Regional Waste Generation Forecasting (2024–2027)</div>
    <div class="section-desc">Audited municipal solid waste generation trends across 12 Maharashtra Urban Local Bodies (ULBs) with Damped Linear Trend projections to 2027.</div>
</div>
""", unsafe_allow_html=True)

if not forecast_df.empty:
    year_col = "target_year" if "target_year" in forecast_df.columns else "forecast_year"
    pred_col = "predicted_tpd" if "predicted_tpd" in forecast_df.columns else "predicted_gen_total_ulb_tpd"

    reg_select_col, reg_stat_col = st.columns([1, 2.5])
    with reg_select_col:
        regions = sorted(forecast_df["region"].unique().tolist())
        selected_reg = st.selectbox("Select District / Municipal Corporation:", regions, index=regions.index("Pune") if "Pune" in regions else 0)

        r_df = forecast_df[forecast_df["region"] == selected_reg].sort_values(by=year_col)
        p2024 = r_df[r_df[year_col] == 2024][pred_col].values
        p2027 = r_df[r_df[year_col] == 2027][pred_col].values
        v2024 = float(p2024[0]) if len(p2024) > 0 else 0.0
        v2027 = float(p2027[0]) if len(p2027) > 0 else 0.0
        net_diff = v2027 - v2024

        st.metric("2024 Projected Load", f"{v2024:,.1f} TPD")
        st.metric("2027 Projected Load", f"{v2027:,.1f} TPD", delta=f"{net_diff:+,.1f} TPD")
        st.caption("Empirical prediction interval evaluated at ±1.96σ confidence bounds.")

    with reg_stat_col:
        cols_plot = [pred_col]
        for b in ["lower_tpd", "upper_tpd"]:
            if b in r_df.columns: cols_plot.append(b)
        chart_df = r_df.set_index(year_col)[cols_plot]
        chart_df.columns = ["Forecast (TPD)", "Lower Bound (-1.96σ)", "Upper Bound (+1.96σ)"][:len(cols_plot)]
        st.line_chart(chart_df)

    # 2024–2027 Full Ledger Table with Net Change and Growth Rate (Model Column Removed)
    st.markdown("#### 📋 2024–2027 Municipal Waste Projections Ledger (All 12 ULBs)")
    
    # Accurate Net Change Ledger
    piv = forecast_df.pivot(index="region", columns=year_col, values=pred_col).round(1)
    if 2027 in piv.columns and 2024 in piv.columns:
        piv["Net Change by 2027 (TPD)"] = (piv[2027] - piv[2024]).apply(lambda x: f"{x:+,.1f} TPD ↗" if x > 0 else f"{x:+,.1f} TPD ↘")
        piv["Annual Growth Rate"] = ((piv[2027] - piv[2024]) / 3).apply(lambda x: f"{x:+,.1f} TPD/yr")
    
    st.dataframe(piv, use_container_width=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 3: Interactive Maharashtra Geospatial Map
# -----------------------------------------------------------------------------
st.markdown("""
<div class="section-box">
    <div class="section-title">🗺️ Maharashtra Municipal Solid Waste Intelligence Map</div>
    <div class="section-desc">Interactive geographic distribution of waste generation and treatment load across 12 major urban local bodies.</div>
</div>
""", unsafe_allow_html=True)

map_html = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; background: #111827; }
        #map { height: 420px; width: 100%; border-radius: 10px; }
        .leaflet-popup-content-wrapper { background: #1f2937; color: #f8fafc; border: 1px solid #374151; }
        .leaflet-popup-tip { background: #1f2937; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([19.7515, 75.7139], 6);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; CartoDB &copy; OpenStreetMap',
            maxZoom: 18
        }).addTo(map);

        var districts = [
            { name: "Mumbai", lat: 19.0760, lon: 72.8777, tpd: 6690, color: "#ef4444" },
            { name: "Pune", lat: 18.5204, lon: 73.8567, tpd: 4439, color: "#f59e0b" },
            { name: "Nagpur", lat: 21.1458, lon: 79.0882, tpd: 1688, color: "#10b981" },
            { name: "Thane", lat: 19.2183, lon: 72.9781, tpd: 2148, color: "#f59e0b" },
            { name: "Nashik", lat: 19.9975, lon: 73.7898, tpd: 2245, color: "#f59e0b" },
            { name: "Aurangabad", lat: 19.8762, lon: 75.3433, tpd: 1858, color: "#10b981" },
            { name: "Kalyan", lat: 19.2437, lon: 73.1355, tpd: 1606, color: "#10b981" },
            { name: "Navi Mumbai", lat: 19.0330, lon: 73.0297, tpd: 743, color: "#10b981" },
            { name: "Kolhapur", lat: 16.7050, lon: 74.2433, tpd: 823, color: "#10b981" },
            { name: "Amravati", lat: 20.9374, lon: 77.7796, tpd: 809, color: "#10b981" },
            { name: "Raigad", lat: 18.5158, lon: 73.1822, tpd: 593, color: "#10b981" },
            { name: "Chandrapur", lat: 19.9615, lon: 79.2961, tpd: 503, color: "#10b981" }
        ];

        districts.forEach(function(d) {
            var circle = L.circleMarker([d.lat, d.lon], {
                color: d.color,
                fillColor: d.color,
                fillOpacity: 0.7,
                radius: Math.max(7, Math.sqrt(d.tpd) / 3.2)
            }).addTo(map);

            circle.bindPopup("<b>" + d.name + "</b><br>Generation: " + d.tpd.toLocaleString() + " TPD<br>Action: Municipal Interventions Active");
        });
    </script>
</body>
</html>
"""
components.html(map_html, height=440)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 4: AI Recommendation Simulator
# -----------------------------------------------------------------------------
st.markdown("""
<div class="section-box">
    <div class="section-title">🧠 Interactive AI Recommendation & Carbon Offset Simulator</div>
    <div class="section-desc">Simulate circular economic yield, scrap valuation, and CO₂ avoidance for any custom material category and batch weight.</div>
</div>
""", unsafe_allow_html=True)

s_c1, s_c2 = st.columns(2)
with s_c1:
    s_class = st.selectbox(
        "Select Material Stream:",
        ["Cardboard", "Food Organics", "Glass", "Metal", "Paper", "Plastic", "Textile Trash", "Vegetation", "Miscellaneous Trash"]
    )
    s_weight = st.slider("Batch Weight (in Kilograms):", 5.0, 5000.0, 250.0, step=10.0)
    s_cond = st.radio("Physical Condition:", ["clean", "contaminated", "wet"], horizontal=True)

# Calculations
rec_info = get_recycling_potential(s_class)
avg_price_map = {"Metal": 140.0, "Plastic": 32.0, "Cardboard": 13.0, "Paper": 10.0, "Glass": 5.0, "Textile Trash": 8.0, "Food Organics": 5.5, "Vegetation": 4.0, "Miscellaneous Trash": 1.5}
avg_price = avg_price_map.get(s_class, 12.0)
val_inr = avg_price * s_weight
co2_mult = {"Metal": 9.2, "Plastic": 1.8, "Cardboard": 1.4, "Paper": 1.3, "Glass": 0.6, "Textile Trash": 3.2, "Food Organics": 0.8, "Vegetation": 0.6, "Miscellaneous Trash": 0.1}.get(s_class, 1.0)
co2_val = round(s_weight * co2_mult, 1)

buyers = rec_info.get("buyer_industries", ["Secondary Recyclers"])
primary_buyer = buyers[0] if buyers else "Regional Industrial Offtakers"

with s_c2:
    st.markdown(f"""
    <div class="res-card" style="border-left: 4px solid #10b981;">
        <div style="font-size: 0.8rem; color: #10b981; font-weight: 700;">ESTIMATED BATCH YIELD</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #ffffff;">₹ {val_inr:,.2f}</div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
            • <b>Est. Carbon Avoidance:</b> <span style="color: #10b981;">{co2_val:,.1f} kg CO₂</span><br>
            • <b>Recyclability Purity:</b> {rec_info.get('recyclability_index', 80)}% ({rec_info.get('economic_viability', 'High')})<br>
            • <b>Degradation Tolerance:</b> {rec_info.get('lifecycle_loops', '5-7 cycles')}<br>
            • <b>Primary Commercial Buyer:</b> {primary_buyer}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 5: 5-Step Circular Recycling SOP
# -----------------------------------------------------------------------------
st.markdown("""
<div class="section-box">
    <div class="section-title">🔄 5-Step Circular Recycling SOP (SWM Rules 2016)</div>
    <div class="section-desc">Statutory standard operating procedures for municipal authorities, MRFs, and EPR registered recyclers.</div>
</div>
""", unsafe_allow_html=True)

sop_c1, sop_c2, sop_c3, sop_c4, sop_c5 = st.columns(5)
with sop_c1:
    st.markdown("""
    <div class="kpi-card" style="padding: 14px;">
        <div style="font-size: 0.75rem; color: #10b981; font-weight: 700;">STEP 01</div>
        <div style="font-weight: 700; color: #fff; margin: 4px 0;">Source Segregation</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">Clean at source. Assign Green (Wet), Blue (Dry), or Black (Inert) bins.</div>
    </div>
    """, unsafe_allow_html=True)

with sop_c2:
    st.markdown("""
    <div class="kpi-card" style="padding: 14px;">
        <div style="font-size: 0.75rem; color: #3b82f6; font-weight: 700;">STEP 02</div>
        <div style="font-weight: 700; color: #fff; margin: 4px 0;">Collection & Transfer</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">Partitioned tippers prevent re-mixing with GPS municipal monitoring.</div>
    </div>
    """, unsafe_allow_html=True)

with sop_c3:
    st.markdown("""
    <div class="kpi-card" style="padding: 14px;">
        <div style="font-size: 0.75rem; color: #f59e0b; font-weight: 700;">STEP 03</div>
        <div style="font-weight: 700; color: #fff; margin: 4px 0;">MRF Optical Sorting</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">NIR sensors and magnetic separators isolate high-value polymers and alloys.</div>
    </div>
    """, unsafe_allow_html=True)

with sop_c4:
    st.markdown("""
    <div class="kpi-card" style="padding: 14px;">
        <div style="font-size: 0.75rem; color: #8b5cf6; font-weight: 700;">STEP 04</div>
        <div style="font-weight: 700; color: #fff; margin: 4px 0;">Industrial Processing</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">Hot caustic washing at 85°C, granulating, extrusion, and induction smelting.</div>
    </div>
    """, unsafe_allow_html=True)

with sop_c5:
    st.markdown("""
    <div class="kpi-card" style="padding: 14px;">
        <div style="font-size: 0.75rem; color: #10b981; font-weight: 700;">STEP 05</div>
        <div style="font-weight: 700; color: #fff; margin: 4px 0;">Circular Offtake (EPR)</div>
        <div style="font-size: 0.75rem; color: #94a3b8;">Direct delivery to certified brand owners for PCR plastic & alloy packaging.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.caption("Smart Waste AI Intelligence • Production Release • PyTorch 2.0+ MobileNetV3 • Streamlit Cloud")
