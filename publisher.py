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

BROKER = "5bedf517a53645328ea3e3a30e67f571.s1.eu.hivemq.cloud"
PORT = 8883
TOPIC = "transport/bus"

USERNAME = "hivemq.webclient.1778944958129"
PASSWORD = "nvPLB<t,$#16Rre9Oa5E"

# ==================================
# CREATE MQTT CLIENT
# ==================================

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(tls_version=ssl.PROTOCOL_TLS)

# ==================================
# CONNECT TO BROKER
# ==================================

client.connect(BROKER, PORT)

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