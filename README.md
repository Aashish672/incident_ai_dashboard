# 🛡️ Incident AI Dashboard

An AI-powered log monitoring and anomaly detection platform built with Django, scikit-learn (Isolation Forest), WebSockets, and a REST API.

---

## ✨ Features

| Feature | Description |
|---|---|
| **AI Anomaly Detection** | Isolation Forest ML model for real-time anomaly scoring |
| **Real-Time Alerts** | WebSocket-powered live notification feed |
| **REST API** | Full CRUD API with Swagger/OpenAPI documentation |
| **Role-Based Access** | Admin/Viewer hierarchy with scoped data access |
| **Dashboard Analytics** | Log trends, hourly heatmaps, level distribution charts |
| **Export** | CSV and PDF report generation |
| **Email Alerts** | Automated SMTP notifications on anomaly detection |
| **Async Processing** | Celery worker for background ML pipeline execution |

---

## 🏗️ Architecture

```
                        ┌──────────────┐
                        │   Browser    │
                        └──────┬───────┘
                               │ HTTP / WebSocket
                        ┌──────▼───────┐
                        │    Nginx     │
                        │ (reverse     │
                        │  proxy)      │
                        └──────┬───────┘
                               │
                  ┌────────────▼────────────┐
                  │       Daphne (ASGI)     │
                  │   Django + Channels     │
                  ├─────────┬──────────────┤
                  │ Views / │  REST API    │
                  │Templates│ (DRF)        │
                  └────┬────┴──────┬───────┘
                       │           │
            ┌──────────▼──┐  ┌─────▼──────┐
            │ PostgreSQL  │  │   Redis     │
            │  (Database) │  │ (Channels + │
            │             │  │  Celery)    │
            └─────────────┘  └─────┬──────┘
                                   │
                            ┌──────▼───────┐
                            │ Celery Worker│
                            │ (ML Pipeline)│
                            │ Isolation    │
                            │ Forest       │
                            └──────────────┘
```

---

## 🛠️ Tech Stack

- **Backend:** Django 5, Django Channels, Django REST Framework
- **ML:** scikit-learn (Isolation Forest), pandas, NumPy
- **Database:** PostgreSQL
- **Task Queue:** Celery + Redis
- **WebSockets:** Django Channels + Redis Channel Layer
- **API Docs:** drf-spectacular (Swagger UI)
- **Frontend:** TailwindCSS, Chart.js
- **Deployment:** Docker, Docker Compose, Nginx, AWS ECS Fargate

---

## 📂 Project Structure

```
incident_ai_dashboard/
├── incident_ai/           # Django project config
│   ├── settings.py        # Centralized settings with env vars
│   ├── celery.py          # Celery app configuration
│   ├── urls.py            # Root URL routing
│   └── asgi.py            # ASGI config for WebSockets
├── logs/                  # Main Django app
│   ├── views/             # Modular views package
│   │   ├── auth.py        # Registration, landing
│   │   ├── dashboard.py   # Analytics dashboard
│   │   ├── upload.py      # CSV upload + async ML
│   │   ├── export.py      # CSV/PDF export
│   │   ├── log_list.py    # Log listing + detail
│   │   ├── notifications.py
│   │   ├── profile.py
│   │   └── health.py      # ALB health check
│   ├── api_views.py       # DRF ViewSets
│   ├── serializers.py     # DRF serializers
│   ├── api_urls.py        # REST API routes
│   ├── tasks.py           # Celery async tasks
│   ├── models.py          # LogEntry, Profile, Notification
│   ├── consumers.py       # WebSocket consumer
│   ├── tests/             # Test suite
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_forms.py
│   │   └── test_api.py
│   └── utils/
│       └── email_utils.py # Anomaly alert emails
├── scripts/
│   └── log_processor.py   # ML pipeline (Isolation Forest)
├── templates/             # Django templates
├── static/                # Static assets
├── deploy/
│   ├── nginx/nginx.conf   # Nginx reverse proxy config
│   └── aws/
│       ├── ecs-task-definition.json
│       └── DEPLOY.md      # AWS deployment guide
├── .github/workflows/
│   └── ci.yml             # GitHub Actions CI/CD
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Node.js (for TailwindCSS, optional)

### Local Development

```bash
# Clone & setup
git clone https://github.com/Aashish672/incident-ai-dashboard.git
cd incident-ai-dashboard
git checkout feature/industry-grade

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values

# Database
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver
```

### With Docker

```bash
cp .env.example .env
# Edit .env
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Visit `http://localhost` (nginx) or `http://localhost:8000` (direct).

---

## 📡 API Documentation

Interactive Swagger UI available at: `http://localhost:8000/api/docs/`

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/logs/` | List logs (paginated, searchable) |
| `POST` | `/api/logs/` | Create a log entry |
| `GET` | `/api/logs/{id}/` | Retrieve a specific log |
| `GET` | `/api/logs/stats/` | Dashboard statistics |
| `GET` | `/api/logs/anomalies/` | Anomaly-only logs |
| `GET` | `/api/notifications/` | List notifications |
| `POST` | `/api/notifications/mark_all_read/` | Mark all read |
| `GET` | `/health/` | Health check (for ALB) |

---

## 🧪 Testing

```bash
python manage.py test --verbosity=2
```

Tests cover:
- **Models**: LogEntry, Profile (role validation), Notification
- **Views**: Access control, response codes, context data, exports
- **Forms**: Registration validation, profile updates
- **API**: CRUD operations, filtering, stats, authentication

---

## ☁️ AWS Deployment

See [deploy/aws/DEPLOY.md](deploy/aws/DEPLOY.md) for step-by-step instructions covering:

- **Option 1:** AWS ECS Fargate (recommended)
- **Option 2:** EC2 with Docker Compose

---

## 🔒 Security

- All secrets via environment variables (never committed)
- HTTPS enforced in production (HSTS, secure cookies)
- CSRF protection with trusted origins
- Role-based access control (Admin/Viewer)
- Non-root Docker container
- Security headers via Nginx

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Aashish Kumar Singh**
- GitHub: [@Aashish672](https://github.com/Aashish672)
- Email: 38aashishkumarsingh11a@gmail.com
