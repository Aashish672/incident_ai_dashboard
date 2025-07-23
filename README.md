# 🚨 Incident AI Dashboard

A powerful AI-enabled incident log monitoring dashboard that detects anomalies in system logs, sends real-time alerts, and provides visual insights using interactive charts and graphs.

---

## 📊 Features

- 📁 Upload CSV log files
- 🤖 AI-based anomaly detection using Isolation Forest
- ✉️ Email alerts on detecting anomalies
- 🔁 Real-time WebSocket updates
- 📈 Interactive dashboard with:
  - Summary cards (total logs, anomalies, log levels)
  - Line chart (Daily trend)
  - Bar chart (Hourly anomalies)
  - Pie chart (Level distribution)
- 📥 Export charts as PNG
- 🧩 Modular Django architecture

---

## 🛠️ Tech Stack

- **Backend:** Django 5.x, Channels, Daphne
- **Frontend:** HTML, TailwindCSS, Chart.js
- **ML:** Pandas, NumPy, Scikit-Learn (Isolation Forest)
- **Real-Time:** Django Channels, WebSockets
- **Email Alerts:** Gmail SMTP (configurable)
- **Deployment-ready:** ASGI compatible

---

## 📂 Folder Structure

incident_ai_dashboard/
│
├── logs/ # Main app
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ ├── templates/
│ └── utils/
│ └── email_utils.py
│
├── dashboard.html # Dashboard UI
├── log_processor.py # AI anomaly detector
├── templates/
│ └── base.html
├── static/
│ └── css, js, ...
├── incident_ai/ # Project config
│ └── settings.py
│
├── manage.py
└── requirements.txt

