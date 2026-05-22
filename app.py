import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="IoT Public Transport Monitoring System",
    page_icon="🚌",
    layout="wide"
)

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

# ---------------- TITLE ----------------
st.title("🚌 IoT Public Transport Monitoring System")
st.markdown("### Real-Time Monitoring and Management Dashboard")

# ---------------- API CONFIG ----------------
API_URL = "https://iot-transport-system-1.onrender.com/telemetry"

# ---------------- FETCH DATA ----------------
try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()

        if len(data) == 0:
            st.warning("No telemetry data received yet.")
            st.stop()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # ---------------- CLEAN DATA ----------------
        numeric_columns = ["lat", "lon", "speed_kmh", "occupancy"]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Convert timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        # ---------------- METRICS ----------------
        st.subheader("📊 System Metrics")

        col1, col2, col3, col4 = st.columns(4)

        total_records = len(df)

        avg_speed = (
            round(df["speed_kmh"].mean(), 2)
            if "speed_kmh" in df.columns
            else 0
        )

        avg_occupancy = (
            round(df["occupancy"].mean(), 2)
            if "occupancy" in df.columns
            else 0
        )

        active_buses = (
            df["bus_id"].nunique()
            if "bus_id" in df.columns
            else 0
        )

        with col1:
            st.metric("Total Records", total_records)

        with col2:
            st.metric("Average Speed", avg_speed)

        with col3:
            st.metric("Average Occupancy", avg_occupancy)

        with col4:
            st.metric("Active Buses", active_buses)

        # ---------------- LIVE TELEMETRY ----------------
        st.subheader("📡 Live Telemetry Data")

        telemetry_columns = [
            "timestamp",
            "trip_id",
            "bus_id",
            "stop_id",
            "lat",
            "lon",
            "speed_kmh",
            "occupancy"
        ]

        available_columns = [
            col for col in telemetry_columns if col in df.columns
        ]

        st.dataframe(
            df[available_columns],
            use_container_width=True
        )

        # ---------------- MAP ----------------
        if "lat" in df.columns and "lon" in df.columns:

            st.subheader("🗺️ Bus Locations")

            map_df = df[["lat", "lon"]].dropna()

            st.map(map_df)

        # ---------------- SPEED ANALYSIS ----------------
        if "speed_kmh" in df.columns:

            st.subheader("🚀 Speed Analysis")

            fig_speed = px.line(
                df,
                x="timestamp",
                y="speed_kmh",
                color="bus_id" if "bus_id" in df.columns else None,
                title="Bus Speed Over Time"
            )

            st.plotly_chart(fig_speed, use_container_width=True)

        # ---------------- OCCUPANCY ANALYSIS ----------------
        if "occupancy" in df.columns:

            st.subheader("👥 Occupancy Analysis")

            fig_occ = px.bar(
                df,
                x=df.index,
                y="occupancy",
                color="bus_id" if "bus_id" in df.columns else None,
                title="Passenger Occupancy"
            )

            st.plotly_chart(fig_occ, use_container_width=True)

        # ---------------- OVERCROWDED BUSES ----------------
        if "occupancy" in df.columns:

            overcrowded = df[df["occupancy"] > 40]

            st.subheader("🚨 Overcrowded Buses")

            if len(overcrowded) > 0:

                st.dataframe(
                    overcrowded[available_columns],
                    use_container_width=True
                )

            else:
                st.success("No overcrowded buses detected.")

        # ---------------- RECENT BUS STATUS ----------------
        if "bus_id" in df.columns:

            st.subheader("🚌 Latest Bus Status")

            latest_status = (
                df.sort_values("timestamp")
                .groupby("bus_id")
                .tail(1)
            )

            status_columns = [
                "bus_id",
                "trip_id",
                "timestamp",
                "speed_kmh",
                "occupancy",
                "stop_id"
            ]

            status_columns = [
                col for col in status_columns if col in latest_status.columns
            ]

            st.dataframe(
                latest_status[status_columns],
                use_container_width=True
            )

    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")