# 🚨 Incident AI Dashboard

**Incident AI Dashboard** is a powerful, AI-enabled log monitoring platform that detects anomalies in system logs, sends real-time email alerts, and visualizes key insights using interactive charts on a beautiful dashboard, powered by Django.

---

## 📊 Features

- 📁 **Upload CSV Log Files**
- 🤖 **AI-Based Anomaly Detection** using Isolation Forest algorithm
- ✉️ **Email Alerts** triggered on detecting anomalies
- 🔁 **Real-Time WebSocket Updates** with Django Channels
- 📈 **Interactive Dashboard** including:
  - Summary Cards (Total Logs, Anomalies, Log Levels)
  - Line Chart (Daily Log Trends)
  - Bar Chart (Anomalies by Hour)
  - Pie Chart (Log Level Distribution)
- 📥 **Exportable Charts** as PNG
- 🧩 **Modular Architecture** using Django

---

## 🛠️ Tech Stack

| Layer          | Technology                                     |
|----------------|------------------------------------------------|
| **Backend**    | Django 5.x, Django Channels, Daphne (ASGI)     |
| **Frontend**   | HTML5, TailwindCSS, Chart.js                   |
| **ML & Data**  | Python, pandas, NumPy, scikit-learn (Isolation Forest) |
| **Real-Time**  | WebSockets via Django Channels                 |
| **Email Alerts**| Gmail SMTP (configurable)                      |
| **Deployment** | ASGI-compatible infrastructure (for real-time) |

---

## 📂 Folder Structure

incident_ai_dashboard/
│
├── logs/ # Main Django app
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ ├── templates/
│ └── utils/
│ └── email_utils.py
│
├── dashboard.html # Main dashboard UI
├── log_processor.py # AI-based anomaly detector
├── templates/
│ └── base.html
├── static/
│ └── css/
│ └── js/
│
├── incident_ai/ # Django project configuration
│ └── settings.py
│
├── manage.py
└── requirements.txt


---

## 🚀 Getting Started

### 1. Clone and Set Up the Project

git clone https://github.com/Aashish672/incident-ai-dashboard.git
cd incident-ai-dashboard

python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

pip install -r requirements.txt


---

### 2. Configure Email Alerts (Gmail SMTP)

Inside `incident_ai/settings.py`, add your Gmail SMTP credentials:

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'


✅ You must enable **[App Passwords](https://myaccount.google.com/security)** if you use 2FA with your Google account.

---

### 3. Run Database Migrations

python manage.py makemigrations
python manage.py migrate



---

### 4. Start the Development Server


🖥️ Visit your dashboard at: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Sample CSV Log Format

timestamp,level,message,source
2025-07-21T14:32:00,INFO,System started,server1
2025-07-21T14:35:00,ERROR,Failed to connect to DB,server2
2025-07-21T14:40:00,CRITICAL,Disk full warning,server3



Upload these files via the dashboard UI to begin processing and visualization.

---

## 🔧 Custom Commands

Manually trigger the log processor from the Django shell:

python manage.py shell
>>> from log_processor import run
>>> run()


---

## 📈 Dashboard Features Preview

- ✅ Total Logs Processed
- ❗ Anomalies Detected by AI
- ⏰ Visual Trends Over Time
- 🥧 Log Level Breakdown
- 📊 Hourly Anomaly Trends

_All charts are exportable as image (PNG) for reporting purposes._

---

## ✅ Roadmap (Week 1 Goals)

- [x] CSV Upload & Parsing
- [x] ML Anomaly Detection
- [x] Email Alerts on Anomaly
- [x] Dashboard Visualizations
- [x] Real-Time WebSocket Integration
- [ ] (Optional) Celery for Background Tasks
- [ ] (Optional) Cron/Task Scheduler Integration

---

## 🤝 Contributing

Contributions, ideas, and issues are welcome!

- Fork the repository
- Create a new branch (`git checkout -b feature/your-feature`)
- Commit your changes (`git commit -am 'Add new feature'`)
- Push to your branch (`git push origin feature/your-feature`)
- Open a Pull Request with a brief description

---
## 📬 Contact

For support, questions, or collaboration, feel free to reach out:

📧 **38aashishkumarsingh11a@gmail.com@gmail.com**  
🔗 GitHub: [https://github.com/Aashish672](https://github.com/Aashish672)

---

> Built with ❤️ using Django, WebSockets, Chart.js, and AI.
