```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

BROKER = os.getenv("BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TOPIC = os.getenv("TOPIC")

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# SQLITE DATABASE
# =========================

conn = sqlite3.connect("transport.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_id TEXT,
    timestamp TEXT,
    lat REAL,
    lon REAL,
    speed_kmh REAL,
    occupancy INTEGER
)
""")

conn.commit()

# =========================
# MQTT CALLBACKS
# =========================

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(TOPIC)
    print(f"Subscribed to {TOPIC}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        print("Received:", payload)

        cursor.execute("""
        INSERT INTO telemetry (
            bus_id,
            timestamp,
            lat,
            lon,
            speed_kmh,
            occupancy
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload.get("bus_id"),
            payload.get("timestamp"),
            payload.get("lat"),
            payload.get("lon"),
            payload.get("speed_kmh"),
            payload.get("occupancy")
        ))

        conn.commit()

    except Exception as e:
        print("Error processing message:", e)

# =========================
# START MQTT CLIENT
# =========================

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, MQTT_PORT)

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
    SELECT
        bus_id,
        timestamp,
        lat,
        lon,
        speed_kmh,
        occupancy
    FROM telemetry
    ORDER BY id DESC
    LIMIT 100
    """)

    rows = cursor.fetchall()

    telemetry = []

    for row in rows:
        telemetry.append({
            "bus_id": row[0],
            "timestamp": row[1],
            "lat": row[2],
            "lon": row[3],
            "speed_kmh": row[4],
            "occupancy": row[5]
        })

    return telemetry
```
