from dotenv import load_dotenv

load_dotenv()

import pandas as pd
import json
import time
import ssl
import paho.mqtt.client as mqtt

# ==================================
# LOAD LOCATION DATA
# ==================================

df = pd.read_csv("data/location_log.csv")

# ==================================
# HIVEMQ CLOUD SETTINGS
# ==================================
import os

BROKER = os.getenv("BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TOPIC = os.getenv("TOPIC")
# ==================================
# CREATE MQTT CLIENT
# ==================================

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(tls_version=ssl.PROTOCOL_TLS)

# ==================================
# CONNECT TO BROKER
# ==================================

client.connect(BROKER, MQTT_PORT)

print("Connected to HiveMQ Cloud")

# ==================================
# STREAM TELEMETRY
# ==================================

for _, row in df.iterrows():

    payload = {
        "timestamp": str(row["timestamp"]),
        "trip_id": row["trip_id"],
        "bus_id": row["bus_id"],
        "stop_id": row["stop_id"],
        "lat": row["lat"],
        "lon": row["lon"],
        "speed_kmh": row["speed_kmh"],
        "occupancy": row["occupancy"]
    }

    client.publish(TOPIC, json.dumps(payload))

    print(f"Published: {payload}")

    time.sleep(1)