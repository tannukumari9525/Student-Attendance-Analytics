"""
Attendance service: percentage computation and defaulter detection.
"""
from sqlalchemy.orm import Session as DBSession

from models.attendance import AttendanceRecord, AttendanceStatus
from models.session import Session as SessionModel
from models.enrollment import Enrollment


def get_attendance_percentage(db: DBSession, student_id: int, course_id: int) -> float:
    """Return attendance % for a student in a course. Returns 0.0 if no sessions."""
    total_sessions = (
        db.query(SessionModel)
        .filter(SessionModel.course_id == course_id)
        .count()
    )
    if total_sessions == 0:
        return 0.0

    present_or_late = (
        db.query(AttendanceRecord)
        .join(SessionModel, AttendanceRecord.session_id == SessionModel.id)
        .filter(
            AttendanceRecord.student_id == student_id,
            SessionModel.course_id == course_id,
            AttendanceRecord.status.in_([AttendanceStatus.present, AttendanceStatus.late]),
        )
        .count()
    )
    return round(present_or_late / total_sessions * 100, 2)


def get_defaulters(db: DBSession, course_id: int, threshold: float = 75.0) -> list[dict]:
    """Return list of students below attendance threshold for a course."""
    enrollments = (
        db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    )
    defaulters = []
    for enrollment in enrollments:
        pct = get_attendance_percentage(db, enrollment.student_id, course_id)
        if pct < threshold:
            defaulters.append(
                {
                    "student_id": enrollment.student_id,
                    "student_name": enrollment.student.name,
                    "attendance_percentage": pct,
                }
            )
    return defaulters
