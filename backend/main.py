from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth as auth_router
from routers import departments as departments_router
from routers import courses as courses_router
from routers import users as users_router
from routers import sessions as sessions_router
from routers import attendance as attendance_router
from routers import leaves as leaves_router
from routers import notifications as notifications_router
from routers import analytics as analytics_router
from routers import reports as reports_router

app = FastAPI(title="Student Attendance Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(departments_router.router, prefix="/api")
app.include_router(courses_router.router, prefix="/api")
app.include_router(users_router.router, prefix="/api")
app.include_router(sessions_router.router, prefix="/api")
app.include_router(attendance_router.router, prefix="/api")
app.include_router(leaves_router.router, prefix="/api")
app.include_router(notifications_router.router, prefix="/api")
app.include_router(analytics_router.router, prefix="/api")
app.include_router(reports_router.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
