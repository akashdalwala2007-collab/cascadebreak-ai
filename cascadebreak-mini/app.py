"""
CascadeBreak AI - Climate Disaster Decision Support Dashboard (V2)
==================================================================
AI-Powered Counterfactual Intervention Optimization for Climate Disasters
"Don't just map the flood. Find the intervention that breaks the cascade."

A technical disaster-response decision-support platform optimizing emergency
counterfactual interventions across disrupted urban networks.
Frontend UI Theme: Climate-Tech Dark Intelligence (Navy, Slate, Cyan, Semantic Red/Green/Amber)
"""

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

# Core backend modules (Intentionally Unmodified)
from scenario import (
    get_synthetic_city_nodes,
    get_synthetic_city_roads,
    get_available_scenarios,
    get_scenario_metadata,
)
from cascade_engine import CascadeEngine
from intervention_engine import InterventionEngine
from visualization import create_network_map

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Dark Tactical Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CascadeBreak AI | Disaster Decision Support",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Comprehensive Custom CSS: Climate-Tech / GIS / Disaster Intelligence
st.markdown(
    """
    <style>
    /* Global Base Reset & Fonts */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0B1220 !important;
        color: #F1F5F9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(11, 18, 32, 0.9) !important;
        backdrop-filter: blur(8px);
    }

    /* Sidebar Dark Intelligence Theme */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #24344D !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #24344D !important;
        margin: 1.2rem 0 !important;
    }

    /* Header Styling */
    .hero-container {
        padding: 0.5rem 0 1.2rem 0;
        border-bottom: 1px solid #24344D;
        margin-bottom: 1.8rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(34, 211, 238, 0.1);
        border: 1px solid rgba(34, 211, 238, 0.3);
        color: #22D3EE;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 4px;
        margin-bottom: 0.6rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F1F5F9;
        letter-spacing: -0.025em;
        line-height: 1.15;
        margin: 0 0 0.4rem 0;
    }
    .hero-title span {
        color: #22D3EE;
    }
    .hero-subtitle {
        font-size: 1.02rem;
        font-weight: 400;
        color: #94A3B8;
        letter-spacing: -0.01em;
        margin: 0;
        line-height: 1.4;
    }
    .hero-quote {
        color: #38BDF8;
        font-style: italic;
        font-size: 0.92rem;
        margin-top: 0.4rem;
    }

    /* Section Headers */
    .section-header-wrap {
        display: flex;
        align-items: baseline;
        gap: 12px;
        border-bottom: 1px solid #24344D;
        padding-bottom: 0.5rem;
        margin-top: 2.2rem;
        margin-bottom: 1.1rem;
    }
    .section-tag {
        font-size: 0.75rem;
        font-weight: 800;
        color: #22D3EE;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        background: #111C2E;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #24344D;
    }
    .section-heading {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F1F5F9;
        letter-spacing: -0.01em;
        text-transform: uppercase;
        margin: 0;
    }

    /* Metric Cards */
    .metric-card-box {
        background-color: #111C2E;
        border: 1px solid #24344D;
        border-radius: 8px;
        padding: 14px 16px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card-label {
        font-size: 0.74rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-card-value {
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 4px;
    }
    .metric-card-delta {
        font-size: 0.78rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .delta-danger { color: #EF4444; }
    .delta-warning { color: #F59E0B; }
    .delta-success { color: #22C55E; }
    .delta-neutral { color: #94A3B8; }

    /* Tactical Cascade Flow */
    .cascade-flow-card {
        background: #111C2E;
        border: 1px solid #24344D;
        border-radius: 8px;
        padding: 16px;
    }
    .cascade-flow-step {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 12px;
        background: #0F172A;
        border-radius: 6px;
        margin-bottom: 8px;
        border-left: 3px solid #EF4444;
    }
    .cascade-flow-step.warning { border-left-color: #F59E0B; }
    .cascade-flow-step.info { border-left-color: #22D3EE; }
    .cascade-flow-step.success { border-left-color: #22C55E; }
    .cascade-step-num {
        background: #1E293B;
        color: #F1F5F9;
        font-size: 0.75rem;
        font-weight: 700;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .cascade-step-content {
        font-size: 0.86rem;
        line-height: 1.35;
        color: #CBD5E1;
    }
    .cascade-step-content b {
        color: #F1F5F9;
    }

    /* Priority Action Card (Visual Highlight) */
    .priority-action-card {
        background: linear-gradient(180deg, #111C2E 0%, #0D1626 100%);
        border: 1px solid #22D3EE;
        border-radius: 10px;
        padding: 22px 24px;
        margin-top: 0.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 0 24px rgba(34, 211, 238, 0.10);
    }
    .priority-tag {
        font-size: 0.72rem;
        font-weight: 800;
        color: #22D3EE;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .priority-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #F1F5F9;
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }
    .priority-reason {
        font-size: 0.98rem;
        color: #CBD5E1;
        line-height: 1.55;
        margin-bottom: 16px;
    }
    .priority-badges-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .priority-badge {
        background: #0F172A;
        border: 1px solid #24344D;
        border-radius: 6px;
        padding: 6px 12px;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .priority-badge-label {
        font-size: 0.68rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600;
    }
    .priority-badge-val {
        font-size: 1.05rem;
        font-weight: 700;
        color: #22D3EE;
    }

    /* Fallback Card when no intervention needed */
    .no-action-card {
        background: #111C2E;
        border: 1px dashed #24344D;
        border-radius: 8px;
        padding: 20px;
        margin-top: 0.6rem;
        margin-bottom: 1.2rem;
    }

    /* Map Legend Box */
    .legend-box {
        background: #111C2E;
        border: 1px solid #24344D;
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 0.85rem;
    }
    .legend-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 7px;
        color: #CBD5E1;
    }
    .legend-line {
        width: 22px;
        height: 4px;
        border-radius: 2px;
        flex-shrink: 0;
    }

    /* Explainability Pillar Card */
    .pillar-card {
        background: #111C2E;
        border: 1px solid #24344D;
        border-radius: 8px;
        padding: 16px 18px;
        height: 100%;
    }
    .pillar-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #22D3EE;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .pillar-text {
        font-size: 0.90rem;
        color: #CBD5E1;
        line-height: 1.45;
    }

    /* Streamlit Widget Overrides */
    .stButton > button {
        background-color: #0F172A !important;
        color: #22D3EE !important;
        border: 1px solid #22D3EE !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 1.1rem !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #111C2E !important;
        border-color: #38BDF8 !important;
        box-shadow: 0 0 12px rgba(34, 211, 238, 0.25) !important;
        color: #F1F5F9 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
        border-bottom: 1px solid #24344D !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0F172A !important;
        border: 1px solid #24344D !important;
        border-bottom: none !important;
        border-radius: 6px 6px 0 0 !important;
        color: #94A3B8 !important;
        padding: 6px 16px !important;
        font-size: 0.86rem !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #111C2E !important;
        border-color: #22D3EE !important;
        color: #22D3EE !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #111C2E !important;
        border: 1px solid #24344D !important;
        border-radius: 6px !important;
        color: #F1F5F9 !important;
    }

    /* Dataframe Overrides */
    [data-testid="stDataFrame"] {
        border: 1px solid #24344D !important;
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sidebar: Controls, Scenario Selector & Weights
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:8px; margin-bottom: 4px;">
            <span style="font-size: 1.25rem;">⚡</span>
            <span style="font-size: 1.15rem; font-weight: 800; color: #F1F5F9; letter-spacing: -0.01em;">CASCADEBREAK</span>
            <span style="font-size: 0.70rem; font-weight: 800; color: #22D3EE; background: #111C2E; padding: 2px 6px; border-radius: 4px; border: 1px solid #24344D;">V2</span>
        </div>
        <div style="font-size: 0.80rem; color: #94A3B8; margin-bottom: 1.2rem;">Climate Decision Support System</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;'>1. Disaster Scenario</div>", unsafe_allow_html=True)
    scenarios = get_available_scenarios()
    selected_scenario = st.selectbox(
        "Hazard Preset",
        scenarios,
        index=0,
        label_visibility="collapsed",
        help="Select a deterministic flood scenario to evaluate systemic network disruption.",
    )
    meta = get_scenario_metadata(selected_scenario)
    st.markdown(
        f"""
        <div style="background:#111C2E; border:1px solid #24344D; border-radius:6px; padding:10px 12px; font-size:0.80rem; color:#94A3B8; line-height:1.4; margin-top:6px;">
            <b style="color:#F1F5F9;">Context:</b> {meta['description']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;'>2. Utility Objective Weights</div>", unsafe_allow_html=True)
    st.caption("Demonstration weights — configure response priorities:")

    wp = st.slider(
        "Population Dual Access (wp)",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Weight for restoring access to both hospital and relief hub.",
    )
    wh = st.slider(
        "Hospital Trauma Access (wh)",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="Weight for restoring access to Level-1 trauma hospital.",
    )
    wr = st.slider(
        "Relief Hub Access (wr)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Weight for restoring access to emergency relief logistics hub.",
    )

    tot_w = wp + wh + wr
    if tot_w > 0:
        st.markdown(
            f"""
            <div style="font-size:0.75rem; color:#64748B; background:#0B1220; padding:4px 8px; border-radius:4px; border:1px solid #1E293B;">
                Ratio: <span style="color:#22D3EE;">Pop {wp/tot_w:.2f}</span> • <span style="color:#22D3EE;">Hosp {wh/tot_w:.2f}</span> • <span style="color:#22D3EE;">Relief {wr/tot_w:.2f}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="background:#111C2E; border:1px solid #24344D; border-radius:6px; padding:12px; font-size:0.78rem; color:#94A3B8; line-height:1.45;">
            <b style="color:#F1F5F9;">Operational Boundary:</b><br>
            &bull; Decision support for human commanders<br>
            &bull; Non-destructive simulation sandbox<br>
            &bull; Systemic cascade disruption ranking
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Data Loading & Initialization
# -----------------------------------------------------------------------------
nodes_data = get_synthetic_city_nodes()
roads_data = get_synthetic_city_roads(selected_scenario)

cascade_engine = CascadeEngine(nodes=nodes_data, roads=roads_data)
intervention_engine = InterventionEngine(cascade_engine=cascade_engine)

baseline_summary = cascade_engine.get_baseline_summary()
flooded_metrics = baseline_summary["flooded_metrics"]
pre_flood_metrics = baseline_summary["pre_flood_metrics"]
flooded_roads = baseline_summary["flooded_roads"]
total_pop = baseline_summary["total_population"]

# -----------------------------------------------------------------------------
# Header: Climate-Tech Brand
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-badge">⚡ Climate Disaster Response Intelligence</div>
        <h1 class="hero-title">CASCADEBREAK <span>AI</span></h1>
        <p class="hero-subtitle">AI-Powered Counterfactual Intervention Optimization for Climate Disasters</p>
        <div class="hero-quote">“Don’t just map the flood. Find the intervention that breaks the cascade.”</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Section 1: Flood Scenario & Network Impact
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">01</span>
        <h2 class="section-heading">Flood Scenario & Network Impact</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

with m_col1:
    st.markdown(
        f"""
        <div class="metric-card-box">
            <div class="metric-card-label">Total Population</div>
            <div class="metric-card-value" style="color: #F1F5F9;">{total_pop:,}</div>
            <div class="metric-card-delta delta-neutral">5 Urban Sectors</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col2:
    n_flooded = baseline_summary['flooded_road_count']
    total_r = baseline_summary['total_roads']
    val_col = "#EF4444" if n_flooded > 0 else "#22C55E"
    delta_text = f"−{n_flooded} Blocked" if n_flooded > 0 else "All Corridors Open"
    delta_class = "delta-danger" if n_flooded > 0 else "delta-success"
    st.markdown(
        f"""
        <div class="metric-card-box">
            <div class="metric-card-label">Flooded Roads</div>
            <div class="metric-card-value" style="color: {val_col};">{n_flooded} <span style="font-size:1rem;color:#94A3B8;">/ {total_r}</span></div>
            <div class="metric-card-delta {delta_class}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col3:
    pop_no_hosp = flooded_metrics["pop_without_hospital"]
    val_col = "#EF4444" if pop_no_hosp > 0 else "#22C55E"
    delta_text = f"−{pop_no_hosp:,} Isolated" if pop_no_hosp > 0 else "All Connected"
    delta_class = "delta-danger" if pop_no_hosp > 0 else "delta-success"
    st.markdown(
        f"""
        <div class="metric-card-box">
            <div class="metric-card-label">Cut Off From Hospital</div>
            <div class="metric-card-value" style="color: {val_col};">{pop_no_hosp:,}</div>
            <div class="metric-card-delta {delta_class}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col4:
    pop_no_relief = flooded_metrics["pop_without_relief"]
    val_col = "#EF4444" if pop_no_relief > 0 else "#22C55E"
    delta_text = f"−{pop_no_relief:,} Isolated" if pop_no_relief > 0 else "All Connected"
    delta_class = "delta-danger" if pop_no_relief > 0 else "delta-success"
    st.markdown(
        f"""
        <div class="metric-card-box">
            <div class="metric-card-label">Cut Off From Relief Hub</div>
            <div class="metric-card-value" style="color: {val_col};">{pop_no_relief:,}</div>
            <div class="metric-card-delta {delta_class}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col5:
    fully_isolated = flooded_metrics["pop_fully_isolated"]
    num_comp = flooded_metrics['num_connected_components']
    val_col = "#EF4444" if fully_isolated > 0 else "#22C55E"
    delta_text = f"{num_comp} Disconnected Subgraphs"
    delta_class = "delta-danger" if num_comp > 1 else "delta-success"
    st.markdown(
        f"""
        <div class="metric-card-box">
            <div class="metric-card-label">Completely Isolated</div>
            <div class="metric-card-value" style="color: {val_col};">{fully_isolated:,}</div>
            <div class="metric-card-delta {delta_class}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Disruption Details Expander
with st.expander("🔍 Inspect Road Failure Inventory & Population Cluster Access Details", expanded=False):
    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#F1F5F9; margin-bottom:8px;'>Impassable Flooded Corridors:</div>", unsafe_allow_html=True)
        if flooded_roads:
            for fr in flooded_roads:
                st.markdown(
                    f"""
                    <div style="background:#0F172A; border-left:3px solid #EF4444; padding:8px 12px; margin-bottom:6px; border-radius:0 4px 4px 0; font-size:0.82rem;">
                        <b style="color:#F1F5F9;">{fr['road_id']}: {fr['name']}</b><br>
                        <span style="color:#94A3B8;">{fr['condition_note']}</span><br>
                        <span style="color:#64748B;">Effort Index: <b style="color:#22D3EE;">{fr['effort_cost']} pts</b> • Length: {fr['length_km']} km • Damage Factor: {fr['damage_factor']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div style='color:#22C55E; font-size:0.85rem;'>✅ No roads are currently flooded in this scenario.</div>", unsafe_allow_html=True)

    with exp_c2:
        st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#F1F5F9; margin-bottom:8px;'>Population Cluster Access Registry:</div>", unsafe_allow_html=True)
        cluster_rows = []
        for nid, s in flooded_metrics["node_status"].items():
            cluster_rows.append({
                "Cluster": s["name"],
                "Population": f"{s['population']:,}",
                "Trauma Hospital": "Passable" if s["can_reach_hospital"] else "Cut Off",
                "Relief Logistics": "Passable" if s["can_reach_relief"] else "Cut Off",
                "Status": "Full Access" if s["has_dual_access"] else ("Isolated" if s["is_isolated"] else "Partial"),
            })
        st.dataframe(pd.DataFrame(cluster_rows), hide_index=True, use_container_width=True)

# -----------------------------------------------------------------------------
# Section 2: Current Network & Cascade Analysis
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">02</span>
        <h2 class="section-heading">Current Network & Cascade Breakdown</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

map_col, flow_col = st.columns([3.2, 1.8])

with map_col:
    m_base = create_network_map(
        nodes=nodes_data,
        roads=roads_data,
        node_status=flooded_metrics["node_status"],
        title="Disrupted Baseline Network",
    )
    st_folium(m_base, width=None, height=440, key="baseline_map")

with flow_col:
    cp = baseline_summary["cascade_progression"]
    st.markdown(
        f"""
        <div class="cascade-flow-card">
            <div style="font-size:0.85rem; font-weight:700; color:#22D3EE; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;">
                Topological Cascade Breakdown
            </div>
            <div class="cascade-flow-step">
                <div class="cascade-step-num" style="background:#EF4444;">1</div>
                <div class="cascade-step-content"><b>Flood Hazard:</b><br>{cp["step_1_flood_disruption"]}</div>
            </div>
            <div class="cascade-flow-step warning">
                <div class="cascade-step-num" style="background:#F59E0B;">2</div>
                <div class="cascade-step-content"><b>Network Disconnection:</b><br>{cp["step_2_network_fragmentation"]}</div>
            </div>
            <div class="cascade-flow-step">
                <div class="cascade-step-num" style="background:#EF4444;">3</div>
                <div class="cascade-step-content"><b>Critical Inaccessibility:</b><br>{cp["step_3_facility_impact"]}</div>
            </div>
            <div class="cascade-flow-step">
                <div class="cascade-step-num" style="background:#EF4444;">4</div>
                <div class="cascade-step-content"><b>Access Loss Cascade:</b><br>{cp["step_4_population_isolation"]}</div>
            </div>
            <div class="legend-box" style="margin-top: 12px;">
                <div class="legend-row">
                    <div class="legend-line" style="background:#22C55E;"></div>
                    <span><b>Open Road</b> (Accessible)</span>
                </div>
                <div class="legend-row">
                    <div class="legend-line" style="background:#EF4444; border: 1px dashed #EF4444;"></div>
                    <span><b>Flooded Road</b> (Impassable)</span>
                </div>
                <div class="legend-row">
                    <span style="font-size:13px;">🏥</span>
                    <span><b>Hospital</b> • <span style="font-size:13px;">🛡️</span> <b>Relief Hub</b></span>
                </div>
                <div class="legend-row">
                    <div style="width:10px; height:10px; border-radius:50%; background:#22C55E;"></div>
                    <span>Full Access</span>
                    <div style="width:10px; height:10px; border-radius:50%; background:#F59E0B; margin-left:8px;"></div>
                    <span>Partial</span>
                    <div style="width:10px; height:10px; border-radius:50%; background:#EF4444; margin-left:8px;"></div>
                    <span>Isolated</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Section 3: Candidate Interventions Portfolio
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">03</span>
        <h2 class="section-heading">Candidate Interventions Portfolio</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Hypothetical response action modalities evaluated independently against the flooded baseline:")

candidates = intervention_engine.get_candidate_interventions()
cand_summary_list = []
for c in candidates:
    cand_summary_list.append({
        "ID": c["id"],
        "Candidate Action": c["name"],
        "Modality": c["type"],
        "Effort Index": f"{c['effort_cost']} pts",
        "Operational Scope": c["description"],
    })
st.dataframe(pd.DataFrame(cand_summary_list), hide_index=True, use_container_width=True)

# -----------------------------------------------------------------------------
# Section 4: Counterfactual Simulation Lab
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">04</span>
        <h2 class="section-heading">Counterfactual Simulation Lab</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_sim, tab_reroute = st.tabs(["🧪 Interactive Intervention Simulator", "🔀 Active Traffic Rerouting Detour Finder"])

with tab_sim:
    st.markdown("<div style='font-size:0.88rem; color:#94A3B8; margin-bottom:10px;'>Simulate any hypothetical response action independently from the immutable flooded baseline:</div>", unsafe_allow_html=True)
    cand_names = [c["name"] for c in candidates]
    if cand_names:
        selected_cand_name = st.selectbox("Select Candidate Action to Simulate:", cand_names, label_visibility="collapsed")
        target_cand = next(c for c in candidates if c["name"] == selected_cand_name)

        sim_g, sim_m = intervention_engine.simulate_candidate(target_cand)

        delta_p = sim_m["pop_with_both"] - flooded_metrics["pop_with_both"]
        delta_h = sim_m["pop_with_hospital"] - flooded_metrics["pop_with_hospital"]
        delta_r = sim_m["pop_with_relief"] - flooded_metrics["pop_with_relief"]
        iso_rem = sim_m["pop_fully_isolated"]

        s_c1, s_c2, s_c3, s_c4 = st.columns(4)
        with s_c1:
            st.markdown(
                f"""
                <div class="metric-card-box">
                    <div class="metric-card-label">Dual Access Restored (ΔP)</div>
                    <div class="metric-card-value" style="color: #22C55E;">+{delta_p:,}</div>
                    <div class="metric-card-delta delta-success">Residents Reconnected</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s_c2:
            st.markdown(
                f"""
                <div class="metric-card-box">
                    <div class="metric-card-label">Hospital Access Restored (ΔH)</div>
                    <div class="metric-card-value" style="color: #22C55E;">+{delta_h:,}</div>
                    <div class="metric-card-delta delta-success">Trauma Corridors Open</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s_c3:
            st.markdown(
                f"""
                <div class="metric-card-box">
                    <div class="metric-card-label">Relief Access Restored (ΔR)</div>
                    <div class="metric-card-value" style="color: #22C55E;">+{delta_r:,}</div>
                    <div class="metric-card-delta delta-success">Supply Lines Clear</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s_c4:
            st.markdown(
                f"""
                <div class="metric-card-box">
                    <div class="metric-card-label">Isolated Remaining</div>
                    <div class="metric-card-value" style="color: #EF4444;">{iso_rem:,}</div>
                    <div class="metric-card-delta delta-danger">−{flooded_metrics['pop_fully_isolated'] - iso_rem:,} Reduction</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No candidate interventions available in this scenario.")

with tab_reroute:
    st.markdown("<div style='font-size:0.88rem; color:#94A3B8; margin-bottom:10px;'>Verify surviving detour routes between isolated sectors and emergency facilities:</div>", unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    with rc1:
        origin_pop = st.selectbox("Origin Cluster:", list(cascade_engine.population_nodes), format_func=lambda x: f"{x} - {nodes_data[x]['name']}")
    with rc2:
        dest_fac = st.selectbox("Destination Facility:", cascade_engine.hospital_nodes + cascade_engine.relief_nodes, format_func=lambda x: f"{x} - {nodes_data[x]['name']}")

    reroute_info = cascade_engine.find_rerouting_path(origin_pop, dest_fac, use_flooded_graph=True)
    if reroute_info:
        st.markdown(
            f"""
            <div style="background:#0F172A; border:1px solid #22D3EE; border-radius:6px; padding:10px 14px; margin-bottom:10px; font-size:0.88rem;">
                <b style="color:#22D3EE;">✅ Passable Detour Available:</b> Total distance <b>{reroute_info['total_distance_km']} km</b> across <b>{reroute_info['hop_count']} segments</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(pd.DataFrame(reroute_info["segments"]), hide_index=True, use_container_width=True)
    else:
        st.markdown(
            f"""
            <div style="background:#0F172A; border:1px solid #EF4444; border-radius:6px; padding:10px 14px; margin-bottom:10px; font-size:0.88rem; color:#EF4444;">
                <b>❌ Network Disconnection:</b> No open route exists between {nodes_data[origin_pop]['name']} and {nodes_data[dest_fac]['name']} in the flooded network.
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# Section 5: Intervention Ranking Table
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">05</span>
        <h2 class="section-heading">Counterfactual Intervention Ranking</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="font-size:0.86rem; color:#94A3B8; margin-bottom:12px;">
        Candidate interventions ranked dynamically by <b>Utility</b>: humanitarian access restored relative to intervention effort:
        $$\\text{Utility}(i) = \\frac{w_p \\cdot \\Delta P(i) + w_h \\cdot \\Delta H(i) + w_r \\cdot \\Delta R(i)}{\\max(\\text{Effort}(i), 0.1)}$$
    </div>
    """,
    unsafe_allow_html=True,
)

ranking_df = intervention_engine.evaluate_all_interventions(wp=wp, wh=wh, wr=wr)

if not ranking_df.empty:
    display_ranking = ranking_df[
        [
            "intervention",
            "type",
            "delta_population",
            "delta_hospital",
            "delta_relief",
            "effort",
            "utility",
        ]
    ].copy()

    display_ranking.columns = [
        "Intervention Candidate",
        "Modality",
        "Pop. Restored (ΔP)",
        "Hospital Restored (ΔH)",
        "Relief Restored (ΔR)",
        "Effort Index",
        "Utility Score",
    ]

    display_ranking["Pop. Restored (ΔP)"] = display_ranking["Pop. Restored (ΔP)"].apply(lambda x: f"+{int(x):,}")
    display_ranking["Hospital Restored (ΔH)"] = display_ranking["Hospital Restored (ΔH)"].apply(lambda x: f"+{int(x):,}")
    display_ranking["Relief Restored (ΔR)"] = display_ranking["Relief Restored (ΔR)"].apply(lambda x: f"+{int(x):,}")
    display_ranking["Effort Index"] = display_ranking["Effort Index"].apply(lambda x: f"{x} pts")
    display_ranking["Utility Score"] = display_ranking["Utility Score"].apply(lambda x: f"{x:,.2f}")

    st.dataframe(display_ranking, use_container_width=True)
else:
    st.info("No candidate interventions to rank in this scenario.")

# -----------------------------------------------------------------------------
# Section 6: Priority Action Recommendation (The Visual Highlight)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">06</span>
        <h2 class="section-heading">Priority Action Recommendation</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

rec = intervention_engine.get_dynamic_recommendation(wp=wp, wh=wh, wr=wr)

if rec["has_beneficial_intervention"]:
    st.markdown(
        f"""
        <div class="priority-action-card">
            <div class="priority-tag">🎯 PRIORITY ACTION IDENTIFIED</div>
            <div class="priority-title">{rec['title'].replace('RECOMMENDED INTERVENTION: ', '')}</div>
            <div class="priority-reason">
                <b>Operational Recommendation:</b> {rec['explanation']}
            </div>
            <div class="priority-badges-row">
                <div class="priority-badge">
                    <span class="priority-badge-label">Max Utility Score</span>
                    <span class="priority-badge-val">{rec['utility']:,.2f}</span>
                </div>
                <div class="priority-badge">
                    <span class="priority-badge-label">Dual Access Restored</span>
                    <span class="priority-badge-val" style="color: #22C55E;">+{rec['delta_population']:,}</span>
                </div>
                <div class="priority-badge">
                    <span class="priority-badge-label">Effort Index</span>
                    <span class="priority-badge-val" style="color: #F59E0B;">{rec['effort']} pts</span>
                </div>
                <div class="priority-badge">
                    <span class="priority-badge-label">Intervention Type</span>
                    <span class="priority-badge-val" style="font-size:0.95rem; color:#F1F5F9;">{rec['intervention_type']}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="no-action-card">
            <div style="font-size: 1.1rem; font-weight: 700; color: #94A3B8;">⚠️ {rec['title']}</div>
            <p style="color: #64748B; margin: 6px 0 0 0; font-size: 0.88rem;">{rec['message']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Section 7: Before → After Visual Impact
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">07</span>
        <h2 class="section-heading">Before → After Network Impact</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

if rec["has_beneficial_intervention"]:
    best_cand = rec["candidate_obj"]
    G_after, metrics_after = intervention_engine.simulate_candidate(best_cand)

    col_before_map, col_after_map = st.columns(2)

    with col_before_map:
        st.markdown(
            f"""
            <div style="background:#111C2E; border:1px solid #24344D; border-radius:6px; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#EF4444; font-weight:700; font-size:0.85rem;">🔴 BEFORE: Disrupted Baseline</span>
                <span style="color:#94A3B8; font-size:0.75rem;">Without Access: <b style="color:#EF4444;">{flooded_metrics['pop_without_both']:,}</b></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        m_b = create_network_map(
            nodes=nodes_data,
            roads=roads_data,
            node_status=flooded_metrics["node_status"],
            title="Baseline",
        )
        st_folium(m_b, width=None, height=380, key="before_folium")

    with col_after_map:
        st.markdown(
            f"""
            <div style="background:#111C2E; border:1px solid #22D3EE; border-radius:6px; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#22D3EE; font-weight:700; font-size:0.85rem;">🔵 AFTER: Post-Intervention</span>
                <span style="color:#94A3B8; font-size:0.75rem;">Without Access: <b style="color:#22C55E;">{metrics_after['pop_without_both']:,}</b></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        m_a = create_network_map(
            nodes=nodes_data,
            roads=roads_data,
            node_status=metrics_after["node_status"],
            title="After Intervention",
            highlight_roads=best_cand.get("target_roads", []),
            extra_edges=best_cand.get("temporary_links", []),
        )
        st_folium(m_a, width=None, height=380, key="after_folium")
else:
    st.info("Select an active disruption scenario to view Before vs After network states.")

# -----------------------------------------------------------------------------
# Section 8: Explainability Analysis
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">08</span>
        <h2 class="section-heading">Why Did CascadeBreak Choose This?</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

if rec["has_beneficial_intervention"]:
    exp_c1, exp_c2, exp_c3 = st.columns(3)
    with exp_c1:
        st.markdown(
            f"""
            <div class="pillar-card">
                <div class="pillar-title">1. Bottleneck Liberation</div>
                <div class="pillar-text">
                    Simulated action breaks the primary cut between subgraphs, reconnecting 
                    <b style="color:#22D3EE;">{rec['delta_population']:,}</b> residents and reducing network fragmentation.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with exp_c2:
        st.markdown(
            f"""
            <div class="pillar-card">
                <div class="pillar-title">2. Resource Efficiency</div>
                <div class="pillar-text">
                    At an Effort Index of <b style="color:#F59E0B;">{rec['effort']} pts</b>, it achieves a Utility of 
                    <b style="color:#22D3EE;">{rec['utility']:,.1f}</b>, maximizing systemic access restoration per deployed resource unit.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with exp_c3:
        st.markdown(
            f"""
            <div class="pillar-card">
                <div class="pillar-title">3. Critical Facility Safeguarding</div>
                <div class="pillar-text">
                    Re-establishes hospital trauma access for <b style="color:#22C55E;">+{rec['delta_hospital']:,}</b> citizens and 
                    relief logistics corridors for <b style="color:#22C55E;">+{rec['delta_relief']:,}</b> evacuees.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.write("No active intervention selected.")

# -----------------------------------------------------------------------------
# Section 9: Strategy Benchmark (Heuristics vs Cascade Optimization)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">09</span>
        <h2 class="section-heading">Strategy Benchmark: Heuristics vs Cascade Optimization</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Demonstrating why systemic topological optimization outperforms traditional operational heuristics:")

baseline_comp_df = intervention_engine.evaluate_baseline_heuristics_comparison(wp=wp, wh=wh, wr=wr)
if not baseline_comp_df.empty:
    st.dataframe(baseline_comp_df, hide_index=True, use_container_width=True)
else:
    st.info("No disruptions to benchmark.")

# -----------------------------------------------------------------------------
# Section 10: System Reliability & Limitations
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="section-header-wrap">
        <span class="section-tag">10</span>
        <h2 class="section-heading">System Reliability & Operational Boundaries</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

rel = intervention_engine.get_analysis_reliability()

r_col1, r_col2 = st.columns([1.5, 2.5])
with r_col1:
    st.markdown(
        f"""
        <div class="metric-card-box">
            <div class="metric-card-label">Prototype Reliability</div>
            <div class="metric-card-value" style="color: #22C55E;">{rel['level']}</div>
            <div style="font-size:0.75rem; color:#94A3B8; margin-top:4px;">{rel['label']}</div>
            <div style="font-size:0.80rem; color:#CBD5E1; margin-top:8px;">{rel['explanation']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with r_col2:
    st.markdown(
        """
        <div class="metric-card-box">
            <div class="metric-card-label">Stage 2 Production Roadmap</div>
            <div style="font-size:0.82rem; color:#CBD5E1; line-height:1.45; margin-top:6px;">
                &bull; <b>Human Decision-Maker:</b> System acts as an advisory intelligence tool for emergency commanders.<br>
                &bull; <b>Real Geospatial Feeds:</b> Stage 2 integrates <b>Sentinel-1 SAR</b> (flood water masks), <b>Copernicus DEM</b> (terrain), <b>OpenStreetMap</b> (road network), and <b>WorldPop</b> (spatial population).<br>
                &bull; <b>ML Road Failure Classifier:</b> Predicts probabilistic failure states P(Failure | X) from hydrological and environmental covariates.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
