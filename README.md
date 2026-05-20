# IoT Transport Monitoring System

## Overview

The IoT Transport Monitoring System is a real-time intelligent transportation platform developed for monitoring and managing public transport data in Ogun State, Nigeria. The system uses Internet of Things (IoT) technologies, MQTT communication protocol, cloud computing, FastAPI backend services, and Streamlit dashboard analytics to monitor public transport operations in real time.

The project was developed as part of a Master of Science (M.Sc.) research work in Information Technology at National Open University of Nigeria.

---

# Objectives

The main objectives of the project are:

* To monitor public transport vehicles in real time
* To track bus locations using GPS telemetry
* To analyze passenger occupancy levels
* To detect overcrowded buses
* To provide transport analytics and visualization
* To improve public transport management using IoT technologies

---

# System Architecture

```text
publisher.py
      ↓
HiveMQ Cloud MQTT Broker
      ↓
FastAPI Backend (main.py)
      ↓
SQLite Database
      ↓
Streamlit Dashboard (app.py)
```

---

# Technologies Used

| Technology      | Purpose                     |
| --------------- | --------------------------- |
| Python          | Core programming language   |
| MQTT            | IoT telemetry communication |
| HiveMQ Cloud    | MQTT cloud broker           |
| FastAPI         | Backend API framework       |
| Streamlit       | Real-time dashboard         |
| SQLite          | Database storage            |
| Pandas          | Data processing             |
| Uvicorn         | ASGI server                 |
| GitHub          | Version control             |
| Render          | Backend deployment          |
| Streamlit Cloud | Dashboard deployment        |

---

# Features

* Real-time vehicle telemetry streaming
* GPS location tracking
* Passenger occupancy monitoring
* Speed analytics
* Overcrowding detection
* Transport data visualization
* Cloud-based IoT architecture
* Real-time dashboard analytics

---

# Project Structure

```text
iot_transport_system/
│
├── data/
│   ├── location_log.csv
│   ├── passenger_log.csv
│   ├── stops.csv
│   └── trips.csv
│
├── screenshots/
│
├── publisher.py
├── main.py
├── app.py
├── requirements.txt
├── README.md
└── transport.db
```

---

# Installation Guide

## Step 1 — Clone Repository

```bash
git clone https://github.com/yourusername/iot-transport-monitoring-system.git
```

---

## Step 2 — Navigate to Project Folder

```bash
cd iot-transport-monitoring-system
```

---

## Step 3 — Create Virtual Environment

### Windows

```bash
python -m venv venv
```

---

## Step 4 — Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

---

## Step 5 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the System

## Start MQTT Publisher

```bash
python publisher.py
```

---

## Start FastAPI Backend

```bash
python -m uvicorn main:app --reload
```

---

## Start Streamlit Dashboard

```bash
python -m streamlit run app.py
```

---

# API Endpoint

## Telemetry Endpoint

```text
http://127.0.0.1:8000/telemetry
```

---

# Dashboard Features

The dashboard provides:

* Live telemetry table
* Active bus count
* Occupancy analysis
* Speed analytics
* Overcrowding detection
* GPS map visualization
* Real-time transport monitoring

---

# Deployment

## Backend Deployment

Backend API is deployed using:

[Render](https://render.com?utm_source=chatgpt.com)

---

## Dashboard Deployment

Dashboard is deployed using:

[Streamlit Cloud](https://streamlit.io/cloud?utm_source=chatgpt.com)

---

## MQTT Broker

MQTT communication uses:

[HiveMQ Cloud](https://www.hivemq.com/mqtt-cloud-broker/?utm_source=chatgpt.com)

---

# Research Contribution

This research contributes to intelligent transportation systems by demonstrating how IoT technologies can be used for:

* smart mobility
* transport analytics
* real-time monitoring
* passenger management
* intelligent public transportation systems

---

# Future Improvements

Future enhancements may include:

* Mobile application integration
* AI-based traffic prediction
* Advanced route optimization
* Real GPS hardware deployment
* Cloud database migration
* Multi-city transport monitoring

---

# Author

M.Sc. Information Technology Research Project

National Open University of Nigeria

---

# License

This project is for academic and research purposes only.
