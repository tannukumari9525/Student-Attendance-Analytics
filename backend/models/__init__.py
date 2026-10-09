# Import all models here so that Alembic autogenerate can detect them
from models.department import Department
from models.user import User
from models.course import Course
from models.enrollment import Enrollment
from models.session import Session
from models.attendance import AttendanceRecord
from models.leave_request import LeaveRequest
from models.notification import Notification

__all__ = [
    "Department",
    "User",
    "Course",
    "Enrollment",
    "Session",
    "AttendanceRecord",
    "LeaveRequest",
    "Notification",
]
