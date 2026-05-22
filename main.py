import json
from fastapi import FastAPI
import paho.mqtt.client as mqtt
import sqlite3
import ssl


app = FastAPI()

import sqlite3

# Create database and telemetry table
conn = sqlite3.connect("transport.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_id TEXT,
    trip_id TEXT,
    stop_id TEXT,
    timestamp TEXT,
    lat REAL,
    lon REAL,
    speed_kmh REAL,
    occupancy INTEGER
)
""")

conn.commit()
conn.close()

# =========================
# MQTT CONFIGURATION
# =========================

BROKER = "5bedf517a53645328ea3e3a30e67f571.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
USERNAME = "ADMIN"
PASSWORD = "AdminBus123"
TOPIC = "transport/bus"

# Store telemetry
telemetry_data = []

# =========================
# MQTT CALLBACKS
# =========================

def on_connect(client, userdata, flags, rc):
    print("\nMQTT Connected with result code:", rc)

    if rc == 0:
        print("Successfully connected to HiveMQ Cloud")
        client.subscribe(TOPIC)
        print("Subscribed to topic:", TOPIC)

    elif rc == 5:
        print("Authentication failed - check username/password")

    else:
        print("Connection failed")


def on_message(client, userdata, msg):
    global telemetry_data

    try:
        payload = msg.payload.decode()

        print("\nReceived MQTT Message:")
        print(payload)

        data = json.loads(payload)

        telemetry_data.append(data)

        # Keep latest 100 records only
        telemetry_data = telemetry_data[-100:]

    except Exception as e:
        print("Error processing message:", e)


# =========================
# MQTT CLIENT SETUP
# =========================

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

# Required for HiveMQ Cloud SSL
client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to HiveMQ Cloud...")

client.connect(BROKER, MQTT_PORT, 60)

client.loop_start()

# =========================
# FASTAPI ROUTES
# =========================

@app.get("/")
def home():
    return {
        "message": "IoT Transport API Running"
    }


@app.get("/telemetry")
def get_telemetry():

    try:
        conn = sqlite3.connect("transport.db")
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM telemetry
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        return {"error": str(e)}

        if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 10000))

    uvicorn.run(app, host="0.0.0.0", port=port)