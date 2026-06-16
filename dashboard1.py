import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="IoT Transport Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .stApp {
            background-color: white;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)


# ----------------------------
# DATABASE
# ----------------------------
conn = sqlite3.connect("transport.db", check_same_thread=False)


def load_data():
    query = """
    SELECT bus_id, trip_id, stop_id, timestamp, lat, lon
    FROM telemetry
    ORDER BY timestamp DESC
    """
    df = pd.read_sql_query(query, conn)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


df = load_data()


# ----------------------------
# HEADER
# ----------------------------
st.title("🚍 IoT Transport Monitoring Dashboard")

if df.empty:
    st.warning("No telemetry data available yet.")
    st.stop()


# ----------------------------
# KPI CARDS
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", len(df))
col2.metric("Active Buses", df["bus_id"].nunique())
col3.metric("Trips Logged", df["trip_id"].nunique())
col4.metric("Latest Update", df["timestamp"].max().strftime("%H:%M:%S"))


# ----------------------------
# LATEST BUS LOCATIONS (MAP)
# ----------------------------
st.subheader("🗺️ Live Bus Map (Abeokuta)")

latest = df.sort_values("timestamp").groupby("bus_id").tail(1)

# Clean data
map_df = latest.dropna(subset=["lat", "lon"])

# FORCE CENTER ON ABEOKUTA
fig = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    hover_name="bus_id",
    hover_data=["trip_id"],
    zoom=12,
    center={"lat": 7.15, "lon": 3.35}
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# TABLE VIEW
# ----------------------------
st.subheader("📍 Latest Bus Data")

st.dataframe(
    latest[["bus_id", "trip_id", "lat", "lon", "timestamp"]],
    use_container_width=True,
    hide_index=True
)


# ----------------------------
# CHART: BUS ACTIVITY ONLY
# ----------------------------
st.subheader("📊 Bus Activity Overview")

bus_counts = df["bus_id"].value_counts().reset_index()
bus_counts.columns = ["bus_id", "records"]

fig = px.bar(
    bus_counts,
    x="bus_id",
    y="records",
    title="Records per Bus"
)

st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# FULL DATA
# ----------------------------
st.subheader("📦 Telemetry Data (Latest 100 Records)")

st.dataframe(df.head(100), use_container_width=True, hide_index=True)


# ----------------------------
# FOOTER
# ----------------------------
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")