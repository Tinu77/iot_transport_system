from fastapi import FastAPI
import sqlite3
import json
import ssl
import paho.mqtt.client as mqtt

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

# =========================
# DATABASE SETUP
# =========================

conn = sqlite3.connect("transport.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    trip_id TEXT,
    bus_id TEXT,
    stop_id TEXT,
    lat REAL,
    lon REAL,
    speed_kmh REAL,
    occupancy INTEGER
)
""")

conn.commit()

# =========================
# HIVEMQ SETTINGS
# =========================

BROKER = "5bedf517a53645328ea3e3a30e67f571.s1.eu.hivemq.cloud"
PORT = 8883
TOPIC = "transport/bus"

USERNAME = "hivemq.webclient.1778946132206"
PASSWORD = "hn9<0JA1@CSG?Xpxd#7e"

# =========================
# MQTT CALLBACK
# =========================

def on_message(client, userdata, msg):

    payload = json.loads(msg.payload.decode())

    print("Received:", payload)

    cursor.execute("""
    INSERT INTO telemetry (
        timestamp,
        trip_id,
        bus_id,
        stop_id,
        lat,
        lon,
        speed_kmh,
        occupancy
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload["timestamp"],
        payload["trip_id"],
        payload["bus_id"],
        payload["stop_id"],
        payload["lat"],
        payload["lon"],
        payload["speed_kmh"],
        payload["occupancy"]
    ))

    conn.commit()

# =========================
# MQTT CLIENT
# =========================

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(tls_version=ssl.PROTOCOL_TLS)

client.on_message = on_message

client.connect(BROKER, PORT)

client.subscribe(TOPIC)

client.loop_start()

print("MQTT Subscriber Running")

# =========================
# API ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "IoT Transport API Running"}

@app.get("/telemetry")
def get_telemetry():

    cursor.execute("""
    SELECT * FROM telemetry
    ORDER BY id DESC
    LIMIT 100
    """)

    rows = cursor.fetchall()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "timestamp": row[1],
            "trip_id": row[2],
            "bus_id": row[3],
            "stop_id": row[4],
            "lat": row[5],
            "lon": row[6],
            "speed_kmh": row[7],
            "occupancy": row[8]
        })

    return results