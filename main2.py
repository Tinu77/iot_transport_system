
import json
import sqlite3
import ssl
from datetime import datetime

from fastapi import FastAPI
import paho.mqtt.client as mqtt
import uvicorn

# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="IoT Transport Monitoring API",
    version="1.0"
)

# =====================================================
# DATABASE
# =====================================================

DB_NAME = "transport.db"

def init_database():

    conn = sqlite3.connect(DB_NAME)
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

init_database()

# =====================================================
# HIVEMQ CLOUD CONFIGURATION
# =====================================================

BROKER = "5bedf517a53645328ea3e3a30e67f571.s1.eu.hivemq.cloud"
PORT = 8883

USERNAME = "ADMIN"
PASSWORD = "AdminBus123"

TOPIC = "transport/bus"

# =====================================================
# MQTT CALLBACKS
# =====================================================

def on_connect(client, userdata, flags, rc):

    print(f"\nMQTT Connected | RC={rc}")

    if rc == 0:

        client.subscribe(TOPIC, qos=1)

        print(f"Subscribed to: {TOPIC}")

    else:

        print("MQTT connection failed")


def on_disconnect(client, userdata, rc):

    print(f"\nMQTT Disconnected | RC={rc}")


def on_message(client, userdata, msg):

    print("\n================================")
    print("🔥 MQTT MESSAGE RECEIVED")
    print("================================")

    try:

        payload = msg.payload.decode()

        print("TOPIC:", msg.topic)
        print("PAYLOAD:", payload)

        data = json.loads(payload)

        bus_id = data.get("bus_id")
        trip_id = data.get("trip_id")
        stop_id = data.get("stop_id")
        timestamp = data.get("timestamp")
        lat = data.get("lat")
        lon = data.get("lon")
        speed_kmh = data.get("speed_kmh")
        occupancy = data.get("occupancy")

        if bus_id is None:
            print("❌ Missing bus_id")
            return

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO telemetry (
                bus_id,
                trip_id,
                stop_id,
                timestamp,
                lat,
                lon,
                speed_kmh,
                occupancy
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bus_id,
            trip_id,
            stop_id,
            timestamp,
            lat,
            lon,
            speed_kmh,
            occupancy
        ))

        conn.commit()
        conn.close()

        print("✅ Saved to database")

    except Exception as e:

        print("❌ MQTT ERROR:", e)

# =====================================================
# MQTT CLIENT
# =====================================================

client = mqtt.Client()

client.username_pw_set(
    USERNAME,
    PASSWORD
)

# Same TLS config as publisher.py
client.tls_set(
    cert_reqs=ssl.CERT_NONE
)

client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

print("Connecting to HiveMQ Cloud...")

client.connect(
    BROKER,
    PORT,
    60
)

client.loop_start()

# =====================================================
# API ROUTES
# =====================================================

@app.get("/")
def home():

    return {
        "status": "running",
        "service": "IoT Transport Monitoring API",
        "time": datetime.now().isoformat()
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.get("/telemetry")
def telemetry():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM telemetry
        ORDER BY id DESC
        LIMIT 100
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


@app.get("/latest")
def latest():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM telemetry
        WHERE id IN (
            SELECT MAX(id)
            FROM telemetry
            GROUP BY bus_id
        )
        ORDER BY bus_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10001
    )

