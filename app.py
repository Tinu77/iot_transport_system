import streamlit as st
import pandas as pd
import requests
import time

# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="IoT Transport Dashboard",
    layout="wide"
)

# =========================================
# PAGE TITLE
# =========================================

st.title("🚌 IoT Public Transport Monitoring System")

st.markdown(
    "### Real-Time Monitoring and Management Dashboard"
)

# =========================================
# AUTO REFRESH CONTAINER
# =========================================

placeholder = st.empty()

# =========================================
# LIVE DASHBOARD LOOP
# =========================================

while True:

    try:

        # =========================================
        # FETCH TELEMETRY DATA FROM API
        # =========================================

        response = requests.get(
            "http://127.0.0.1:8000/telemetry"
        )

        data = response.json()

        df = pd.DataFrame(data)

        with placeholder.container():

            # =========================================
            # LIVE TELEMETRY TABLE
            # =========================================

            st.subheader("📡 Live Telemetry Data")

            st.dataframe(
                df,
                use_container_width=True
            )

            # =========================================
            # KPI METRICS
            # =========================================

            st.subheader("📊 System Metrics")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Records",
                len(df)
            )

            col2.metric(
                "Average Speed",
                round(df["speed_kmh"].mean(), 2)
            )

            col3.metric(
                "Average Occupancy",
                round(df["occupancy"].mean(), 2)
            )

            col4.metric(
                "Active Buses",
                df["bus_id"].nunique()
            )

            # =========================================
            # OVERCROWDED BUSES
            # =========================================

            st.subheader("🚨 Overcrowded Buses")

            crowded = df[df["occupancy"] > 40]

            if len(crowded) > 0:

                st.dataframe(
                    crowded,
                    use_container_width=True
                )

            else:

                st.success(
                    "No overcrowded buses detected."
                )

            # =========================================
            # OCCUPANCY ANALYSIS
            # =========================================

            st.subheader("👥 Occupancy Analysis")

            st.bar_chart(df["occupancy"])

            # =========================================
            # SPEED ANALYSIS
            # =========================================

            st.subheader("🚍 Speed Analysis")

            st.line_chart(df["speed_kmh"])

            # =========================================
            # SPEED DISTRIBUTION
            # =========================================

            st.subheader("📈 Speed Distribution")

            st.area_chart(df["speed_kmh"])

            # =========================================
            # TRIPS PER BUS
            # =========================================

            st.subheader("🛣 Trips Per Bus")

            trip_counts = df["bus_id"].value_counts()

            st.bar_chart(trip_counts)

            # =========================================
            # LIVE GPS MAP
            # =========================================

            st.subheader("🗺 Live Bus Locations")

            map_df = df[["lat", "lon"]]

            st.map(map_df)

            # =========================================
            # LAST UPDATE TIME
            # =========================================

            st.caption(
                "Dashboard auto-refreshes every 5 seconds."
            )

    except Exception as e:

        st.error(f"Error loading dashboard: {e}")

    # =========================================
    # REFRESH EVERY 5 SECONDS
    # =========================================

    time.sleep(5)