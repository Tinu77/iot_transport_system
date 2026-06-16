import pandas as pd
import json
import time
import ssl
import random
import paho.mqtt.client as mqtt

# =========================
# MQTT CONFIGURATION
# =========================

BROKER = "5bedf517a53645328ea3e3a30e67f571.s1.eu.hivemq.cloud"
PORT = 8883
TOPIC = "transport/bus"

USERNAME = "ADMIN"
PASSWORD = "AdminBus123"

# =========================
# LOAD CSV
# =========================

df = pd.read_csv("transport_data.csv")

print("CSV Loaded Successfully")
print(df.head())

# =========================
# MQTT CALLBACKS
# =========================

def on_connect(client, userdata, flags, rc):
    print("\nMQTT CONNECTION RESULT:", rc)

    if rc == 0:
        print("Successfully connected to HiveMQ Cloud")

    elif rc == 5:
        print("Authentication failed - check username/password")

    else:
        print("Connection failed")


def on_disconnect(client, userdata, rc):
    print("\nDisconnected with result code:", rc)

# =========================
# CREATE MQTT CLIENT
# =========================

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# =========================
# CONNECT
# =========================

print("\n========== MQTT CONFIG ==========")
print("BROKER:", BROKER)
print("PORT:", PORT)
print("USERNAME:", USERNAME)
print("TOPIC:", TOPIC)
print("=================================\n")

print("Connecting to HiveMQ Cloud...")

client.connect(BROKER, PORT, 60)

client.loop_start()

time.sleep(3)

# =========================
# BUS FLEET
# =========================

buses = [
    "BUS001",
    "BUS002",
    "BUS003",
    "BUS004",
    "BUS005",
    "BUS006",
    "BUS007",
    "BUS008",
    "BUS009",
    "BUS010"
]

# =========================
# CONTINUOUS PUBLISHING
# =========================

print("\nStarting Fleet Simulation...\n")

while True:

    for _, row in df.iterrows():

        for i, bus in enumerate(buses):

            payload = {
                "bus_id": bus,
                "trip_id": f"TRIP_{bus}",
                "timestamp": str(row["timestamp"]),

                # Slightly different location for each bus
                "lat": float(row["lat"]) + (i * 0.005),
                "lon": float(row["lon"]) + (i * 0.005),

                # Slight speed variation
                "speed_kmh": round(
                    float(row["speed_kmh"]) +
                    random.uniform(-5, 5),
                    2
                ),

                # Random occupancy
                "occupancy": random.randint(5, 50)
            }

            result = client.publish(
                TOPIC,
                json.dumps(payload)
            )

            print("Published:", payload)

            if result.rc == 0:
                print("Message sent successfully")
            else:
                print("Failed to send message")

            time.sleep(0.5)

    print("\nCompleted Route - Restarting...\n")