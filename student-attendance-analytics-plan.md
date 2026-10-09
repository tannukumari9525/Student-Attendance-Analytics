# Student Attendance Analytics — MVP Plan

## Top-Level Overview

Build a full-stack web application for student attendance tracking and analytics that runs entirely on localhost.

- **Backend:** Python 3.11+ with FastAPI, SQLite (via SQLAlchemy ORM), JWT authentication
- **Frontend:** React 18 + TypeScript, Recharts for visualizations, Axios for API calls
- **Auth:** JWT tokens with role-encoded claims (admin, teacher, student, parent)
- **Database:** SQLite — single file, zero setup, committed to the repo for dev convenience

### User Roles Supported
| Role | Key Capabilities |
|---|---|
| Admin | Manage users, courses, departments, academic calendar |
| Teacher | Mark attendance, view class analytics, approve leave requests |
| Student | View own attendance, apply for leave, view notifications |
| Parent | Read-only view of linked child's attendance |

### Features in Scope (MVP)
- Role-based login (JWT)
- Attendance marking (manual per session, bulk CSV upload)
- Analytics dashboards (per role: charts, heatmap, trends, defaulter list)
- Leave request workflow (student applies → teacher approves/rejects)
- Parent view (linked to student record)
- Notification center (in-app alerts for threshold breaches, leave status)
- Export reports (CSV, PDF)

---

## Project Structure

```
student-attendance-analytics/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── auth/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── context/
│   │   └── types/
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffolding & Environment Setup

**Status:** [x] done

**Intent**
Establish the repo structure, install dependencies, and verify that both the FastAPI backend and React frontend start successfully on localhost with a health-check endpoint and a blank home page.

**Expected Outcomes**
- `backend/` folder with FastAPI app running on `http://localhost:8000`
- `frontend/` folder with React + TypeScript app running on `http://localhost:5173` (Vite)
- `GET /api/health` returns `{ "status": "ok" }`
- CORS configured so the frontend can call the backend
- SQLite database file created on first backend start

**Todo List**
1. Create `backend/` directory; initialise `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `alembic`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`, `pydantic[email]`
2. Create `backend/main.py` with FastAPI app instance, CORS middleware (allow `http://localhost:5173`), and `/api/health` route
3. Create `backend/database.py` — SQLAlchemy engine pointing to `./attendance.db`, `SessionLocal`, `Base`
4. Scaffold `backend/models/`, `backend/schemas/`, `backend/routers/`, `backend/services/`, `backend/auth/` as empty packages
5. Initialise Alembic (`alembic init alembic`) and configure `alembic.ini` to use the SQLite URL
6. Create `frontend/` using `npm create vite@latest frontend -- --template react-ts`
7. Install frontend dependencies: `axios`, `react-router-dom`, `recharts`, `@types/recharts`, `tailwindcss`, `date-fns`, `react-hot-toast`
8. Configure Tailwind CSS in the frontend
9. Add a Vite proxy rule so `/api` requests forward to `http://localhost:8000`
10. Write a `README.md` with local setup commands for both backend and frontend

**Relevant Context**
- FastAPI docs: https://fastapi.tiangolo.com
- Vite proxy: `vite.config.ts` → `server.proxy`

---

### Sub-Task 2 — Database Models & Migrations

**Status:** [x] done

**Intent**
Define all SQLAlchemy ORM models that represent the full data domain and generate the initial Alembic migration to create the SQLite schema.

**Expected Outcomes**
- All tables created in `attendance.db` after running `alembic upgrade head`
- Models cover: User, Department, Course, Enrollment, Session, AttendanceRecord, LeaveRequest, Notification

**Todo List**
1. Create `backend/models/user.py` — `User` table: `id`, `name`, `email`, `hashed_password`, `role` (enum: admin/teacher/student/parent), `department_id`, `linked_student_id` (nullable, for parent role), `is_active`, `created_at`
2. Create `backend/models/department.py` — `Department`: `id`, `name`, `code`
3. Create `backend/models/course.py` — `Course`: `id`, `name`, `code`, `department_id`, `teacher_id`, `credits`, `semester`, `academic_year`
4. Create `backend/models/enrollment.py` — `Enrollment`: `id`, `student_id`, `course_id`, `enrolled_at` (many-to-many junction)
5. Create `backend/models/session.py` — `Session`: `id`, `course_id`, `date`, `start_time`, `end_time`, `session_type` (enum: lecture/lab/seminar/tutorial), `conducted_by`
6. Create `backend/models/attendance.py` — `AttendanceRecord`: `id`, `session_id`, `student_id`, `status` (enum: present/absent/late/excused), `marked_by`, `marked_at`, `notes`
7. Create `backend/models/leave_request.py` — `LeaveRequest`: `id`, `student_id`, `course_id`, `from_date`, `to_date`, `reason`, `status` (enum: pending/approved/rejected), `reviewed_by`, `reviewed_at`, `created_at`
8. Create `backend/models/notification.py` — `Notification`: `id`, `user_id`, `title`, `body`, `is_read`, `created_at`, `notification_type` (enum: threshold_alert/leave_update/general)
9. Create `backend/models/__init__.py` that imports all models so Alembic can detect them
10. Generate initial Alembic migration: `alembic revision --autogenerate -m "initial_schema"`
11. Run `alembic upgrade head` and verify all tables are created

**Relevant Context**
- All models inherit from `Base` defined in `backend/database.py`
- SQLAlchemy `Enum` type for Python enums
- Alembic `env.py` must import `Base.metadata` from models

---

### Sub-Task 3 — Authentication (JWT)

**Status:** [x] done

**Intent**
Implement JWT-based email/password authentication with role-encoded tokens, protected route dependencies, and a seed script to create an initial admin user.

**Expected Outcomes**
- `POST /api/auth/login` returns `access_token` and `token_type`
- `GET /api/auth/me` returns the current user's profile (protected)
- Role is encoded in the JWT payload and accessible via a FastAPI dependency
- Passwords are hashed with bcrypt
- A seed script creates one user per role for local testing

**Todo List**
1. Create `backend/auth/jwt.py` — `create_access_token(data, expires_delta)`, `decode_token(token)` using `python-jose`
2. Create `backend/auth/dependencies.py` — `get_current_user` FastAPI dependency that extracts and validates the JWT from the `Authorization: Bearer` header; `require_role(*roles)` dependency factory
3. Create `backend/auth/password.py` — `hash_password(plain)`, `verify_password(plain, hashed)` using `passlib`
4. Create `backend/schemas/auth.py` — Pydantic models: `LoginRequest`, `TokenResponse`, `UserProfile`
5. Create `backend/routers/auth.py` — `POST /api/auth/login`, `GET /api/auth/me`
6. Register `auth` router in `main.py`
7. Create `backend/seed.py` — inserts demo users (admin, teacher, student, parent with linked_student_id set) if they do not already exist
8. Test login with `curl` or the FastAPI Swagger UI at `http://localhost:8000/docs`

**Relevant Context**
- JWT secret stored in an env variable `JWT_SECRET` (with a fallback default for dev)
- Token expiry: 24 hours for MVP
- `linked_student_id` on the parent user enables the parent-view feature later

---

### Sub-Task 4 — Core Backend APIs

**Status:** [x] done

**Intent**
Build the REST API endpoints for all domain entities: users, departments, courses, enrollments, sessions, and attendance records. This is the data backbone all dashboard features depend on.

**Expected Outcomes**
- Full CRUD for: Departments, Courses, Sessions
- Enrollment management (add/remove student from course)
- Attendance marking (single record and bulk)
- Bulk CSV upload endpoint for attendance import
- All write endpoints are role-protected

**Todo List**
1. Create Pydantic schemas in `backend/schemas/` for each model (Create, Update, Read variants)
2. Create `backend/routers/departments.py` — CRUD, admin only
3. Create `backend/routers/courses.py` — CRUD (admin/teacher), list enrolled students
4. Create `backend/routers/users.py` — admin: list/create/update/deactivate users; student/parent: read own profile
5. Create `backend/routers/sessions.py` — teacher creates sessions for their course; list sessions by course/date
6. Create `backend/routers/attendance.py`:
   - `POST /api/attendance/` — mark single record (teacher)
   - `POST /api/attendance/bulk` — mark many records for a session at once (teacher)
   - `POST /api/attendance/upload-csv` — parse uploaded CSV file and bulk-insert records (teacher)
   - `GET /api/attendance/session/{session_id}` — list all records for a session
   - `GET /api/attendance/student/{student_id}` — all records for a student (student sees own; parent sees linked child; teacher/admin see any)
   - `PATCH /api/attendance/{record_id}` — correct a record (teacher, with audit note)
7. Create `backend/services/attendance_service.py` — compute attendance percentage per student per course, flag defaulters (below threshold, default 75%)
8. Register all routers in `main.py`
9. Verify all endpoints appear in Swagger UI at `/docs`

**Relevant Context**
- CSV upload uses FastAPI `UploadFile` + Python `csv.DictReader`
- Percentage = (present + late) / total_sessions * 100
- Audit trail: `AttendanceRecord.notes` stores correction reason; `marked_by` stores editor user id

---

### Sub-Task 5 — Leave Request & Notification APIs

**Status:** [x] done

**Intent**
Implement the leave request workflow (student submits, teacher approves/rejects) and the notification system (in-app alerts generated automatically on threshold breach or leave status change).

**Expected Outcomes**
- `POST /api/leaves/` — student submits a leave request
- `PATCH /api/leaves/{id}/review` — teacher approves or rejects
- Approved leaves automatically set related attendance records to `excused` status
- Notifications generated when: student drops below threshold, leave request status changes
- `GET /api/notifications/` — paginated list for the current user
- `PATCH /api/notifications/{id}/read` — mark as read
- `PATCH /api/notifications/read-all` — mark all as read

**Todo List**
1. Create `backend/schemas/leave.py` — `LeaveRequestCreate`, `LeaveRequestReview`, `LeaveRequestRead`
2. Create `backend/schemas/notification.py` — `NotificationRead`
3. Create `backend/routers/leaves.py` — submit, list (student sees own; teacher sees for their courses), review endpoint
4. Create `backend/services/leave_service.py` — on approval, query `AttendanceRecord` rows in the date range for the student/course and update status to `excused`; create a `Notification` for the student
5. Create `backend/routers/notifications.py` — list, mark-read, mark-all-read
6. Create `backend/services/notification_service.py` — `create_notification(user_id, title, body, type)` utility; `check_and_notify_threshold(student_id, course_id)` called after any attendance record is saved
7. Register leave and notification routers in `main.py`

**Relevant Context**
- Threshold check triggers in `attendance_service` after every `POST /api/attendance/` or `POST /api/attendance/bulk` call
- Notification for leave: created in `leave_service` when status changes to approved or rejected
- For MVP, notifications are in-app only (no email/SMS)

---

### Sub-Task 6 — Analytics & Reporting APIs

**Status:** [x] done

**Intent**
Build the API endpoints that power all dashboard charts and the export feature. These are read-only, aggregation-heavy endpoints.

**Expected Outcomes**
- Dashboard summary endpoints per role
- Subject-wise, day-of-week, weekly trend analytics
- Defaulter list endpoint
- CSV and PDF export endpoints

**Todo List**
1. Create `backend/routers/analytics.py` with these endpoints:
   - `GET /api/analytics/summary` — role-aware: admin gets institution stats; teacher gets class stats; student gets personal stats; parent gets child stats
   - `GET /api/analytics/student/{student_id}/courses` — per-course attendance % for a student
   - `GET /api/analytics/course/{course_id}/trend` — weekly attendance % trend (list of week → % pairs)
   - `GET /api/analytics/course/{course_id}/heatmap` — daily attendance data for calendar heatmap
   - `GET /api/analytics/course/{course_id}/day-of-week` — average % per day of week
   - `GET /api/analytics/defaulters?course_id=&threshold=75` — list of students below threshold
   - `GET /api/analytics/course/{course_id}/students` — per-student attendance % ranked
2. Create `backend/services/analytics_service.py` — raw SQL aggregations via SQLAlchemy Core for performance
3. Create `backend/routers/reports.py`:
   - `GET /api/reports/export/csv?course_id=&from=&to=` — streams a CSV file
   - `GET /api/reports/export/pdf?course_id=&student_id=` — generates a simple PDF using `reportlab` (add to requirements.txt)
4. Add `reportlab` to `backend/requirements.txt`

**Relevant Context**
- All analytics endpoints must respect role-based data visibility (teacher only sees their own courses; student only sees own data)
- Trend endpoint groups by ISO week number using SQLite `strftime('%W', date)`
- Heatmap endpoint returns list of `{ date, status, count }` objects

---

### Sub-Task 7 — Frontend: Auth, Routing & Layout

**Status:** [x] done

**Intent**
Build the React application shell: authenticated routing, role-based redirect after login, persistent JWT storage, a shared layout with sidebar navigation, and the login page.

**Expected Outcomes**
- Login page at `/login` — email + password form, calls `POST /api/auth/login`
- JWT stored in `localStorage`; Axios instance attaches it as `Bearer` header automatically
- After login, user is redirected to their role-specific dashboard
- Protected route wrapper redirects unauthenticated users to `/login`
- Shared layout: sidebar with nav links (role-filtered), header with user info and logout, notification bell with unread count

**Todo List**
1. Create `frontend/src/types/index.ts` — TypeScript interfaces: `User`, `Course`, `Session`, `AttendanceRecord`, `LeaveRequest`, `Notification`, `AnalyticsSummary`
2. Create `frontend/src/context/AuthContext.tsx` — stores `user` + `token`, provides `login(email, password)` and `logout()` functions, reads token from `localStorage` on init
3. Create `frontend/src/api/client.ts` — Axios instance with `baseURL: /api`, request interceptor to attach JWT, response interceptor to handle 401 (redirect to login)
4. Create `frontend/src/api/` modules: `auth.ts`, `attendance.ts`, `courses.ts`, `analytics.ts`, `leaves.ts`, `notifications.ts`
5. Create `frontend/src/components/ProtectedRoute.tsx` — redirects to `/login` if no valid token
6. Create `frontend/src/components/Layout.tsx` — sidebar + header shell; sidebar links filtered by user role
7. Create `frontend/src/pages/LoginPage.tsx` — form with email/password, error display, submit calls `AuthContext.login`
8. Set up `frontend/src/App.tsx` with `react-router-dom` routes:
   - `/login` → `LoginPage`
   - `/dashboard` → role-specific dashboard (wrapped in `ProtectedRoute`)
   - `/attendance`, `/leaves`, `/reports`, `/notifications`, `/admin` routes
9. Create a `useNotifications` hook that polls `GET /api/notifications/` every 30 seconds and exposes unread count for the header bell

**Relevant Context**
- Role values from JWT: `admin`, `teacher`, `student`, `parent`
- Sidebar links per role: admin sees all; teacher sees dashboard/attendance/leaves/reports; student sees dashboard/leaves/notifications; parent sees dashboard/notifications

---

### Sub-Task 8 — Frontend: Role Dashboards & Attendance UI

**Status:** [x] done

**Intent**
Build the four role-specific dashboard pages and the attendance marking interface for teachers (the most complex interactive screen).

**Expected Outcomes**
- Admin dashboard: institution-wide summary cards, defaulter count, department breakdown bar chart
- Teacher dashboard: course list with attendance %, defaulter alert count, recent session list
- Student dashboard: attendance % per course as progress rings, heatmap calendar, upcoming shortage warning
- Parent dashboard: same as student dashboard but for the linked child
- Mark Attendance page: teacher selects course + date, sees student roster, marks each student present/absent/late, submits

**Todo List**
1. Create `frontend/src/pages/AdminDashboard.tsx` — summary cards (total students, courses, sessions today, defaulters), bar chart of department-wise attendance using Recharts
2. Create `frontend/src/pages/TeacherDashboard.tsx` — course cards with attendance %, defaulter badge, link to mark attendance; recent sessions table
3. Create `frontend/src/pages/StudentDashboard.tsx` — per-course attendance % shown as a progress ring (SVG or Recharts RadialBar), calendar heatmap, shortage warning banner if any course below threshold
4. Create `frontend/src/pages/ParentDashboard.tsx` — fetches linked child's data and renders the same view as student dashboard with child's name shown
5. Create `frontend/src/pages/MarkAttendancePage.tsx`:
   - Course selector dropdown
   - Date picker
   - On submit of course+date: fetch enrolled students, render a table where each row has the student name and a toggle (Present / Late / Absent)
   - "Mark All Present" button
   - Submit button calls `POST /api/attendance/bulk`
6. Create `frontend/src/pages/AttendancePage.tsx` — view mode: filter by course/date range, paginated table of attendance records
7. Create `frontend/src/components/charts/` — reusable chart components: `AttendancePieChart`, `WeeklyTrendLineChart`, `DayOfWeekBarChart`, `CalendarHeatmap`

**Relevant Context**
- Calendar heatmap: render a grid of day cells for the current semester, colour-coded green/yellow/red based on status
- Progress ring threshold colours: green >= 85%, yellow 75–84%, red < 75%
- Parent page uses `GET /api/analytics/student/{linked_student_id}/courses`

---

### Sub-Task 9 — Frontend: Leave Requests, Notifications & Reports

**Status:** [x] done

**Intent**
Build the remaining feature pages: leave application form, teacher review queue, notification center, and the reports/export page.

**Expected Outcomes**
- Students can submit leave requests with date range, course, and reason
- Teachers see a pending leave queue and can approve or reject with one click
- Notification center lists all in-app notifications, supports mark-as-read
- Reports page allows filtering by course/date range and downloading CSV or PDF

**Todo List**
1. Create `frontend/src/pages/LeavePage.tsx`:
   - Student view: form (course selector, from/to date, reason textarea) + history table of past requests with status badge
   - Teacher view: pending queue table with approve/reject action buttons; past decisions list
2. Create `frontend/src/pages/NotificationsPage.tsx` — list of notifications, unread highlighted, "Mark all read" button, notification type icon
3. Create `frontend/src/pages/ReportsPage.tsx` — filter controls (course, date range, student optional), preview table, "Export CSV" and "Export PDF" buttons that trigger file downloads via `window.open` or `axios` blob response
4. Create `frontend/src/components/LeaveStatusBadge.tsx` — reusable pill badge: pending=yellow, approved=green, rejected=red
5. Create `frontend/src/components/NotificationItem.tsx` — single notification row with icon, title, body, time-ago, read/unread state
6. Wire all new pages into the router in `App.tsx` with appropriate role-based access guards

**Relevant Context**
- File download pattern: `axios.get(url, { responseType: 'blob' })` then create an object URL and trigger an `<a>` click
- PDF download endpoint from Sub-Task 6: `GET /api/reports/export/pdf`
- Leave submission calls `POST /api/leaves/`; review calls `PATCH /api/leaves/{id}/review`

---

### Sub-Task 10 — Admin Panel: User & Course Management

**Status:** [x] done

**Intent**
Build the admin-only screens for managing users (create, deactivate, link parent to student) and managing courses/departments.

**Expected Outcomes**
- Admin can list, create, and deactivate users of any role
- Admin can link a parent user to a student user
- Admin can create and manage departments and courses
- Admin can assign teachers to courses

**Todo List**
1. Create `frontend/src/pages/admin/UserManagementPage.tsx` — table with search/filter by role, "Add User" modal form, deactivate toggle, "Link Parent" action that opens a student-selector modal
2. Create `frontend/src/pages/admin/CourseManagementPage.tsx` — table of courses with department/teacher/semester, "Add Course" modal, edit/delete actions
3. Create `frontend/src/pages/admin/DepartmentPage.tsx` — simple CRUD table for departments
4. Create `frontend/src/components/Modal.tsx` — reusable modal wrapper used across admin forms
5. Register all admin pages under `/admin/*` routes in `App.tsx`, protected by `require_role("admin")` guard on the frontend

**Relevant Context**
- Admin APIs are already built in Sub-Task 4 (`/api/users`, `/api/courses`, `/api/departments`)
- Use React state + `useEffect` pattern (no external state manager needed for MVP)

---

### Sub-Task 11 — Integration Testing & README

**Status:** [x] done

**Intent**
Verify the full end-to-end flow works on localhost using the seeded demo data, fix any integration issues, and write a complete README with setup and run instructions.

**Expected Outcomes**
- Running `python seed.py` populates the database with demo data
- All four role logins work and land on the correct dashboard
- Attendance marking flow works end-to-end (create session → mark → analytics update)
- Leave workflow works end-to-end (student applies → teacher approves → attendance updated)
- Notifications appear after threshold breach
- CSV and PDF exports download correctly
- `README.md` contains complete local setup instructions

**Todo List**
1. Expand `backend/seed.py` to create: 2 departments, 4 courses, 1 teacher per course, 10 students, 1 parent linked to student[0], 30 days of sessions per course, randomised attendance records for each
2. Verify admin dashboard loads with seeded data
3. Verify teacher can mark attendance and analytics update immediately
4. Verify student dashboard shows correct % and heatmap
5. Verify parent dashboard shows linked child's data
6. Verify leave request → teacher approval → attendance excused flow
7. Verify notification bell increments on threshold breach
8. Verify CSV download and PDF download from reports page
9. Update `README.md` with:
   - Prerequisites (Python 3.11+, Node 18+)
   - Backend setup: `python -m venv venv`, activate, `pip install -r requirements.txt`, `alembic upgrade head`, `python seed.py`, `uvicorn main:app --reload`
   - Frontend setup: `npm install`, `npm run dev`
   - Demo login credentials table (email + password for each role)
   - Port reference: backend = 8000, frontend = 5173

**Relevant Context**
- Seed script uses `session.merge()` or checks existence before insert to be idempotent
- FastAPI Swagger UI available at `http://localhost:8000/docs` for manual API testing
