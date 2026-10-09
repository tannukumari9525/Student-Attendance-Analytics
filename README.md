# Student Attendance Analytics

A full-stack web application for student attendance tracking and analytics.

- **Backend:** Python 3.11+ · FastAPI · SQLite (SQLAlchemy ORM) · JWT Authentication
- **Frontend:** React 18 · TypeScript · Tailwind CSS · Recharts · Vite

---

## Features

| Role | Key Capabilities |
|---|---|
| **Admin** | Manage users, courses, departments; view institution-wide analytics |
| **Teacher** | Mark attendance (per session or bulk CSV), approve/reject leave requests, view class analytics, export reports |
| **Student** | View own attendance %, apply for leave, receive threshold alerts |
| **Parent** | Read-only view of linked child's attendance |

- ✅ Role-based JWT login
- ✅ Attendance marking — single record, bulk, CSV upload
- ✅ Analytics dashboards — summary cards, trend charts, defaulter list
- ✅ Leave request workflow (student → teacher approval → auto-excused records)
- ✅ In-app notification center (threshold alerts, leave status updates)
- ✅ CSV and PDF export

---

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |

---

## Local Setup

### 1 — Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (creates attendance.db)
alembic upgrade head

# Seed demo data (departments, courses, students, 30 days of attendance)
python seed.py

# Start the API server
uvicorn main:app --reload
```

Backend runs at **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**

---

### 2 — Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@demo.com | admin123 |
| Teacher | teacher@demo.com | teacher123 |
| Teacher 1 | teacher1@demo.com | teacher123 |
| Student | student@demo.com | student123 |
| Student 01 | student01@demo.com | student123 |
| Parent | parent@demo.com | parent123 |

> The parent account is linked to Student 01.

---

## Project Structure

```
student-attendance-analytics/
├── backend/
│   ├── main.py              # FastAPI app + router registration
│   ├── database.py          # SQLAlchemy engine, SessionLocal, Base
│   ├── seed.py              # Demo data seed script
│   ├── requirements.txt
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # FastAPI route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── departments.py
│   │   ├── courses.py
│   │   ├── sessions.py
│   │   ├── attendance.py
│   │   ├── leaves.py
│   │   ├── notifications.py
│   │   ├── analytics.py
│   │   └── reports.py
│   ├── services/            # Business logic
│   │   ├── attendance_service.py
│   │   ├── leave_service.py
│   │   ├── notification_service.py
│   │   └── analytics_service.py
│   └── auth/
│       ├── jwt.py
│       ├── dependencies.py
│       └── password.py
└── frontend/
    └── src/
        ├── api/             # Axios API modules
        ├── components/      # Shared components (Layout, Modal, etc.)
        ├── context/         # AuthContext
        ├── hooks/           # useNotifications
        ├── pages/           # Page components per route
        │   └── admin/       # Admin-only pages
        └── types/           # TypeScript interfaces
```

---

## API Reference

All routes are prefixed with `/api`. Use the Swagger UI at `/docs` for full reference.

| Method | Path | Description |
|---|---|---|
| POST | /api/auth/login | Email/password login |
| GET | /api/auth/me | Current user profile |
| GET | /api/departments/ | List departments |
| GET | /api/courses/ | List courses |
| GET | /api/sessions/ | List sessions |
| POST | /api/attendance/ | Mark single attendance |
| POST | /api/attendance/bulk | Bulk mark attendance |
| POST | /api/attendance/upload-csv | Import CSV |
| POST | /api/leaves/ | Submit leave request |
| PATCH | /api/leaves/{id}/review | Approve/reject leave |
| GET | /api/notifications/ | Get notifications |
| GET | /api/analytics/summary | Role-aware dashboard summary |
| GET | /api/reports/export/csv | Download CSV report |
| GET | /api/reports/export/pdf | Download PDF report |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET` | `dev-secret-change-in-production` | JWT signing secret |

Set via a `.env` file or shell export before starting uvicorn in production.

---

## Ports

| Service | Port |
|---|---|
| Backend API | 8000 |
| Frontend Dev | 5173 |
