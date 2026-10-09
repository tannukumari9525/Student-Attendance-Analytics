"""
Leave service: on approval, mark related attendance records as excused
and create notification for the student.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession

from models.attendance import AttendanceRecord, AttendanceStatus
from models.leave_request import LeaveRequest, LeaveStatus
from models.notification import NotificationType
from models.session import Session as SessionModel
from services.notification_service import create_notification


def process_leave_approval(db: DBSession, leave: LeaveRequest, reviewer_id: int) -> None:
    """Update attendance records to excused for approved leave."""
    sessions = (
        db.query(SessionModel)
        .filter(
            SessionModel.course_id == leave.course_id,
            SessionModel.date >= leave.from_date,
            SessionModel.date <= leave.to_date,
        )
        .all()
    )
    for session in sessions:
        records = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_id == session.id,
                AttendanceRecord.student_id == leave.student_id,
            )
            .all()
        )
        for record in records:
            record.status = AttendanceStatus.excused
            record.notes = f"Excused via leave request #{leave.id}"
            record.marked_by = reviewer_id
            record.marked_at = datetime.now(timezone.utc)

    # Notify student
    from models.course import Course
    course = db.query(Course).filter(Course.id == leave.course_id).first()
    course_name = course.name if course else f"Course #{leave.course_id}"
    create_notification(
        db,
        user_id=leave.student_id,
        title="Leave Request Approved",
        body=f"Your leave request for {course_name} ({leave.from_date} – {leave.to_date}) has been approved.",
        notification_type=NotificationType.leave_update,
    )


def process_leave_rejection(db: DBSession, leave: LeaveRequest) -> None:
    """Create rejection notification for the student."""
    from models.course import Course
    course = db.query(Course).filter(Course.id == leave.course_id).first()
    course_name = course.name if course else f"Course #{leave.course_id}"
    create_notification(
        db,
        user_id=leave.student_id,
        title="Leave Request Rejected",
        body=f"Your leave request for {course_name} ({leave.from_date} – {leave.to_date}) has been rejected.",
        notification_type=NotificationType.leave_update,
    )
