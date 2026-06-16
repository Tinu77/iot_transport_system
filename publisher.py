import json
import ssl
import time
import random
from datetime import datetime

import paho.mqtt.client as mqtt

# =====================================================
# HIVEMQ CLOUD CONFIGURATION
# =====================================================

BROKER = "5bedf517a53645328ea3e3a30e67f571.s1.eu.hivemq.cloud"
PORT = 8883
TOPIC = "transport/bus"

USERNAME = "ADMIN"
PASSWORD = "AdminBus123"

# =====================================================
# ROUTE A
# =====================================================

ROUTE_A = [
    {"stop_id": "KUTO", "lat": 7.1557, "lon": 3.3451},
    {"stop_id": "PANSEKE", "lat": 7.1650, "lon": 3.3500},
    {"stop_id": "CAMP", "lat": 7.1750, "lon": 3.3600},
    {"stop_id": "ADATAN", "lat": 7.1850, "lon": 3.3700},
    {"stop_id": "LAFENWA", "lat": 7.1950, "lon": 3.3800}
]

# =====================================================
# ROUTE B
# =====================================================

ROUTE_B = [
    {"stop_id": "ITA_EKO", "lat": 7.1580, "lon": 3.3470},
    {"stop_id": "OMIDA", "lat": 7.1605, "lon": 3.3485},
    {"stop_id": "IJAYE", "lat": 7.1680, "lon": 3.3550},
    {"stop_id": "OKE_ILEWO", "lat": 7.1780, "lon": 3.3650},
    {"stop_id": "TOTORO", "lat": 7.1900, "lon": 3.3750}
]

# =====================================================
# BUS FLEET
# =====================================================

BUSES = {
    "BUS001": ROUTE_A,
    "BUS002": ROUTE_A,
    "BUS003": ROUTE_A,
    "BUS004": ROUTE_A,
    "BUS005": ROUTE_A,
    "BUS006": ROUTE_B,
    "BUS007": ROUTE_B,
    "BUS008": ROUTE_B,
    "BUS009": ROUTE_B,
    "BUS010": ROUTE_B
}

# =====================================================
# TRACK BUS POSITIONS
# =====================================================

bus_positions = {}

for i, bus in enumerate(BUSES.keys()):
    bus_positions[bus] = i % 5

# =====================================================
# MQTT CALLBACKS
# =====================================================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to HiveMQ Cloud")
    else:
        print(f"❌ Connection failed. RC={rc}")

def on_disconnect(client, userdata, rc):
    print(f"⚠️ Disconnected. RC={rc}")

# =====================================================
# MQTT CLIENT
# =====================================================
client = mqtt.Client(protocol=mqtt.MQTTv311)


client.username_pw_set(
    USERNAME,
    PASSWORD
)

client.tls_set(
    cert_reqs=ssl.CERT_NONE
)

client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# =====================================================
# CONNECT
# =====================================================

try:

    print("Connecting to HiveMQ Cloud...")

    client.connect(
        BROKER,
        PORT,
        60
    )

    client.loop_start()

    time.sleep(2)

except Exception as e:

    print("Connection Error:", e)
    raise SystemExit

# =====================================================
# START SIMULATION
# =====================================================

print("\n🚌 Starting Abeokuta Smart Transport Simulation\n")

while True:

    for bus, route in BUSES.items():

        position = bus_positions[bus]

        stop = route[position]

        payload = {
            "bus_id": bus,
            "trip_id": f"{bus}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "stop_id": stop["stop_id"],
            "timestamp": datetime.now().isoformat(),
            "lat": round(
                stop["lat"] + random.uniform(-0.0010, 0.0010),
                6
            ),
            "lon": round(
                stop["lon"] + random.uniform(-0.0010, 0.0010),
                6
            ),
            "speed_kmh": round(
                random.uniform(20, 60),
                2
            ),
            "occupancy": random.randint(5, 50)
        }

        result = client.publish(
            TOPIC,
            json.dumps(payload),
            qos=1
        )

        if result.rc == 0:

            print(
                f"{bus} | "
                f"{stop['stop_id']} | "
                f"Speed={payload['speed_kmh']} km/h | "
                f"Passengers={payload['occupancy']}"
            )

        else:

            print(f"❌ Publish failed for {bus}")

        # Move to next stop
        bus_positions[bus] = (
            bus_positions[bus] + 1
        ) % len(route)

        time.sleep(0.5)

    print("\n🔄 Route cycle completed\n")

    time.sleep(3)