import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# =====================================================
# CONFIG
# =====================================================

API_URL = "http://127.0.0.1:10001"

st.set_page_config(
    page_title="Smart Transport System - Abeokuta",
    layout="wide"
)

st.title("🎓 Smart IoT Transport System (Abeokuta Case Study)")

# =====================================================
# SAFE API FUNCTIONS
# =====================================================

def get_latest():
    try:
        res = requests.get(f"{API_URL}/latest", timeout=5)
        return res.json()
    except:
        return []

def get_metrics():
    try:
        res = requests.get(f"{API_URL}/metrics", timeout=5)
        return res.json()
    except:
        return {}

# =====================================================
# LOAD DATA
# =====================================================

latest_data = get_latest()
metrics = get_metrics()

df = pd.DataFrame(latest_data)

# =====================================================
# KPI SECTION
# =====================================================

st.subheader("📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Active Buses", len(df))
col2.metric("Avg Speed (km/h)", metrics.get("avg_speed", 0))
col3.metric("Avg Occupancy", metrics.get("avg_occupancy", 0))
col4.metric("Congested Buses", metrics.get("congested_buses", 0))

st.divider()

# =====================================================
# MAP SECTION (MODERN PLOTLY MAP)
# =====================================================

st.subheader("🗺️ Live Bus Tracking Map")

if not df.empty:

    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        hover_name="bus_id",
        hover_data=["stop_id", "speed_kmh", "occupancy"],
        color="speed_kmh",
        size="occupancy",
        zoom=10,
        height=600
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0)
    )

    fig.update_traces(marker=dict(opacity=0.75))

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No live data yet. Start publisher.py and main.py")

# =====================================================
# TABLE VIEW
# =====================================================

st.subheader("📍 Live Fleet Data")

st.dataframe(df, use_container_width=True)

# =====================================================
# SYSTEM HEALTH
# =====================================================

st.subheader("🧠 System Intelligence Metrics")

st.json(metrics)

# =====================================================
# AUTO REFRESH
# =====================================================

time.sleep(3)
st.rerun()