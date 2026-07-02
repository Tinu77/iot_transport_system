import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="IoT Smart Transport Monitoring",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# AUTO REFRESH EVERY 5 SECONDS
# =====================================================

st_autorefresh(
    interval=5000,
    key="dashboard_refresh"
)

# =====================================================
# API CONFIGURATION
# =====================================================

API_URL = "https://iot-transport-system-1.onrender.com"

LATEST_ENDPOINT = f"{API_URL}/latest"
TELEMETRY_ENDPOINT = f"{API_URL}/telemetry"
HEALTH_ENDPOINT = f"{API_URL}/health"

# =====================================================
# PROFESSIONAL THEME
# =====================================================

st.markdown("""
<style>

.stApp{
    background:#F5F7FA;
}

h1{
    color:#003366;
}

h2{
    color:#003366;
}

div[data-testid="metric-container"]{
    background:white;
    border-radius:12px;
    padding:18px;
    border-left:6px solid #0d6efd;
    box-shadow:0 1px 8px rgba(0,0,0,.10);
}

thead tr th{
    background:#003366 !important;
    color:white !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data(ttl=5)
def load_latest():

    try:

        response = requests.get(
            LATEST_ENDPOINT,
            timeout=15
        )

        response.raise_for_status()

        df = pd.DataFrame(response.json())

        if df.empty:
            return pd.DataFrame()

        numeric_columns = [
            "lat",
            "lon",
            "speed_kmh",
            "occupancy"
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        if "timestamp" in df.columns:

            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                errors="coerce"
            )

        return df

    except Exception as e:

        st.error(f"Latest endpoint error: {e}")

        return pd.DataFrame()


@st.cache_data(ttl=5)
def load_history():

    try:

        response = requests.get(
            TELEMETRY_ENDPOINT,
            timeout=20
        )

        response.raise_for_status()

        df = pd.DataFrame(response.json())

        if df.empty:
            return pd.DataFrame()

        numeric_columns = [
            "lat",
            "lon",
            "speed_kmh",
            "occupancy"
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        if "timestamp" in df.columns:

            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                errors="coerce"
            )

        return df

    except Exception as e:

        st.error(f"Telemetry endpoint error: {e}")

        return pd.DataFrame()

# =====================================================
# GET DATA
# =====================================================

latest = load_latest()

history = load_history()

if latest.empty:

    st.error("Unable to retrieve live bus information from the API.")

    st.stop()

# =====================================================
# API HEALTH
# =====================================================

try:

    requests.get(
        HEALTH_ENDPOINT,
        timeout=5
    )

    api_status = "🟢 ONLINE"

except:

    api_status = "🔴 OFFLINE"

# =====================================================
# HEADER
# =====================================================

left, right = st.columns([4,1])

with left:

    st.title("🚌 IoT Smart Transport Monitoring Dashboard")

    st.caption(
        "Real-Time Public Transport Monitoring System • MSc Thesis Project"
    )

with right:

    st.metric(
        "API Status",
        api_status
    )

# =====================================================
# KPI CARDS
# =====================================================

st.markdown("## 📊 System Overview")

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.metric(
        "Active Buses",
        latest["bus_id"].nunique()
    )

with c2:

    st.metric(
        "Trips",
        latest["trip_id"].nunique()
    )

with c3:

    st.metric(
        "Average Speed",
        f"{latest['speed_kmh'].mean():.1f} km/h"
    )

with c4:

    st.metric(
        "Average Occupancy",
        f"{latest['occupancy'].mean():.0f}"
    )

c5,c6,c7,c8 = st.columns(4)

with c5:

    st.metric(
        "Telemetry Records",
        len(history)
    )

with c6:

    st.metric(
        "Stops Covered",
        latest["stop_id"].nunique()
    )

with c7:

    st.metric(
        "Latest Update",
        latest["timestamp"].max().strftime("%H:%M:%S")
    )

with c8:

    st.metric(
        "Current Time",
        datetime.now().strftime("%H:%M:%S")
    )

st.divider()
# =====================================================
# LIVE BUS MAP (PYDECK)
# =====================================================

st.header("🗺️ Live Bus Locations")

map_df = latest.copy()

# Remove invalid GPS coordinates
map_df = map_df.dropna(subset=["lat", "lon"])

if map_df.empty:

    st.warning("No GPS coordinates available.")

else:

    # Bus information shown when hovering
    map_df["tooltip"] = (
        "<b>Bus:</b> " + map_df["bus_id"] +
        "<br><b>Trip:</b> " + map_df["trip_id"] +
        "<br><b>Stop:</b> " + map_df["stop_id"] +
        "<br><b>Speed:</b> " + map_df["speed_kmh"].round(1).astype(str) + " km/h" +
        "<br><b>Passengers:</b> " + map_df["occupancy"].astype(str)
    )

    # Give every bus the same blue color (can be customized later)
    map_df["r"] = 0
    map_df["g"] = 102
    map_df["b"] = 255

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_radius=120,
        get_fill_color="[r, g, b]",
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=map_df["lat"].mean(),
        longitude=map_df["lon"].mean(),
        zoom=12,
        pitch=35
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "{tooltip}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        },
        map_style="road"
    )

    st.pydeck_chart(deck)

st.divider()

# =====================================================
# LIVE BUS STATUS
# =====================================================

st.header("🚍 Current Bus Status")

display = latest.copy()

display = display.sort_values("bus_id")

display["Speed (km/h)"] = display["speed_kmh"].round(1)
display["Passengers"] = display["occupancy"]
display["Updated"] = display["timestamp"].dt.strftime("%H:%M:%S")

st.dataframe(

    display[
        [
            "bus_id",
            "trip_id",
            "stop_id",
            "Speed (km/h)",
            "Passengers",
            "Updated"
        ]
    ],

    use_container_width=True,
    hide_index=True

)

st.divider()
# =====================================================
# ANALYTICS DASHBOARD
# =====================================================

# =====================================================
# ANALYTICS DASHBOARD
# =====================================================

st.header("📈 Transport Analytics")

# -----------------------------------------------------
# Average Speed by Bus
# -----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("🚀 Average Speed by Bus")

    speed_df = (
        history.groupby("bus_id")["speed_kmh"]
        .mean()
        .reset_index()
    )

    speed_df["Average Speed"] = speed_df["speed_kmh"].round(1)

    fig_speed = px.bar(
        speed_df,
        x="bus_id",
        y="Average Speed",
        color="Average Speed",
        text="Average Speed",
        title="Average Speed (km/h)"
    )

    fig_speed.update_layout(
        height=420,
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_speed, use_container_width=True)

# -----------------------------------------------------
# Passenger Occupancy
# -----------------------------------------------------

with right:

    st.subheader("👥 Average Passenger Occupancy")

    occ_df = (
        history.groupby("bus_id")["occupancy"]
        .mean()
        .reset_index()
    )

    occ_df["Average Occupancy"] = occ_df["occupancy"].round(0)

    fig_occ = px.bar(
        occ_df,
        x="bus_id",
        y="Average Occupancy",
        color="Average Occupancy",
        text="Average Occupancy",
        title="Average Passenger Occupancy"
    )

    fig_occ.update_layout(
        height=420,
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_occ, use_container_width=True)

st.divider()

# =====================================================
# TELEMETRY RECORDS
# =====================================================

left, right = st.columns(2)

with left:

    st.subheader("🚌 Records per Bus")

    records = history["bus_id"].value_counts().reset_index()
    records.columns = ["Bus", "Records"]

    fig_records = px.bar(
        records,
        x="Bus",
        y="Records",
        color="Records",
        text="Records"
    )

    fig_records.update_layout(
        height=420,
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_records, use_container_width=True)

with right:

    st.subheader("🛣 Route Distribution")

    routes = latest["trip_id"].value_counts().reset_index()
    routes.columns = ["Route", "Count"]

    fig_routes = px.pie(
        routes,
        names="Route",
        values="Count",
        hole=0.45
    )

    fig_routes.update_layout(height=420)

    st.plotly_chart(fig_routes, use_container_width=True)

st.divider()

# =====================================================
# SPEED TREND
# =====================================================

st.subheader("📊 Speed Trend")

trend = history.sort_values("timestamp")

fig = px.line(
    trend,
    x="timestamp",
    y="speed_kmh",
    color="bus_id",
    title="Vehicle Speed Over Time"
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# OCCUPANCY TREND
# =====================================================

st.subheader("👥 Passenger Occupancy Trend")

fig = px.line(
    trend,
    x="timestamp",
    y="occupancy",
    color="bus_id",
    title="Passenger Occupancy Over Time"
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------------------------------
# Row 2 - Records and Routes
# -----------------------------------------------------

col3, col4 = st.columns(2)

with col3:

    st.subheader("🚌 Telemetry Records per Bus")

    count_df = (
        history["bus_id"]
        .value_counts()
        .reset_index()
    )

    count_df.columns = ["bus_id", "records"]

    fig_count = px.bar(
        count_df,
        x="bus_id",
        y="records",
        color="records",
        text="records"
    )

    fig_count.update_layout(
        coloraxis_showscale=False,
        height=420
    )

    st.plotly_chart(fig_count, use_container_width=True)


with col4:

    st.subheader("🛣 Route Distribution")

    route_df = (
        latest["trip_id"]
        .value_counts()
        .reset_index()
    )

    route_df.columns = ["trip_id", "count"]

    fig_route = px.pie(
        route_df,
        names="trip_id",
        values="count",
        hole=0.45
    )

    fig_route.update_layout(
        height=420
    )

    st.plotly_chart(fig_route, use_container_width=True)

st.divider()

# -----------------------------------------------------
# Row 3 - Speed Trend
# -----------------------------------------------------

st.subheader("📊 Speed Trend")

trend = history.copy()

trend = trend.sort_values("timestamp")

fig_trend = px.line(
    trend,
    x="timestamp",
    y="speed_kmh",
    color="bus_id",
    markers=True,
    labels={
        "timestamp": "Time",
        "speed_kmh": "Speed (km/h)"
    }
)

fig_trend.update_layout(
    height=500
)

st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# -----------------------------------------------------
# Row 4 - Occupancy Trend
# -----------------------------------------------------

st.subheader("👥 Passenger Occupancy Trend")

fig_occ_trend = px.line(
    trend,
    x="timestamp",
    y="occupancy",
    color="bus_id",
    markers=True,
    labels={
        "timestamp": "Time",
        "occupancy": "Passengers"
    }
)

fig_occ_trend.update_layout(
    height=500
)

st.plotly_chart(fig_occ_trend, use_container_width=True)

st.divider()
# =====================================================
# LIVE TELEMETRY TABLE
# =====================================================

st.header("📋 Live Telemetry")

search = st.text_input(
    "🔍 Search Bus ID",
    ""
)

table = history.copy()

if search:

    table = table[
        table["bus_id"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

table = table.sort_values(
    "timestamp",
    ascending=False
)

show_columns = [
    "bus_id",
    "trip_id",
    "stop_id",
    "timestamp",
    "lat",
    "lon",
    "speed_kmh",
    "occupancy"
]

st.dataframe(

    table[show_columns],

    use_container_width=True,
    hide_index=True,
    height=450

)

st.divider()

# =====================================================
# DOWNLOAD DATA
# =====================================================

st.header("📥 Export Telemetry")

csv = table.to_csv(index=False).encode("utf-8")

st.download_button(

    label="⬇ Download CSV",

    data=csv,

    file_name="transport_telemetry.csv",

    mime="text/csv"

)

st.divider()

# =====================================================
# SYSTEM INFORMATION
# =====================================================

st.header("🖥️ System Information")

left, right = st.columns(2)

with left:

    st.info(f"""
Backend API

• URL: {API_URL}

• Status: {api_status}

• Auto Refresh: Every 5 Seconds

• Database: SQLite

• Protocol: MQTT over TLS

• Broker: HiveMQ Cloud

""")

with right:

    st.success(f"""
Dashboard Statistics

Total Records: {len(history)}

Active Buses: {latest['bus_id'].nunique()}

Routes: {latest['trip_id'].nunique()}

Stops: {latest['stop_id'].nunique()}

Average Speed: {latest['speed_kmh'].mean():.2f} km/h

Average Occupancy: {latest['occupancy'].mean():.1f}
""")

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

footer_left, footer_mid, footer_right = st.columns([2, 2, 2])

with footer_left:

    st.caption("🎓 MSc Research Project")

with footer_mid:

    st.caption(
        "Department of Computer Science"
    )

with footer_right:

    st.caption(
        f"Last Refresh: {datetime.now().strftime('%d %b %Y %H:%M:%S')}"
    )

st.markdown(
"""
<center>

<b>IoT Smart Transport Monitoring System</b><br>

Real-Time Public Transport Monitoring Using MQTT, FastAPI, SQLite, Streamlit and HiveMQ Cloud

</center>
""",
unsafe_allow_html=True
)