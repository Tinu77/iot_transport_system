import pandas as pd
import json
import time
import ssl
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

# Required for HiveMQ Cloud
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
print("PASSWORD:", PASSWORD)
print("TOPIC:", TOPIC)
print("=================================\n")

print("Connecting to HiveMQ Cloud...")

client.connect(BROKER, PORT, 60)

client.loop_start()

time.sleep(3)

# =========================
# PUBLISH DATA
# =========================

for _, row in df.iterrows():

    payload = {
        "bus_id": str(row["bus_id"]),
        "timestamp": str(row["timestamp"]),
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "speed_kmh": float(row["speed_kmh"]),
        "occupancy": int(row["occupancy"])
    }

    result = client.publish(TOPIC, json.dumps(payload))

    print("\nPublished:", payload)

    print("MQTT Result Code:", result.rc)

    if result.rc == 0:
        print("Message sent successfully")

    else:
        print("Failed to send message")

    time.sleep(2)

client.loop_stop()
client.disconnect()