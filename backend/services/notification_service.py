"""
Notification utility service.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession

from models.notification import Notification, NotificationType
from services.attendance_service import get_attendance_percentage


def create_notification(
    db: DBSession,
    user_id: int,
    title: str,
    body: str,
    notification_type: NotificationType,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        title=title,
        body=body,
        notification_type=notification_type,
        created_at=datetime.now(timezone.utc),
    )
    db.add(notif)
    db.flush()
    return notif


def check_and_notify_threshold(
    db: DBSession, student_id: int, course_id: int, threshold: float = 75.0
) -> None:
    """Create a threshold alert notification if the student drops below threshold."""
    from models.course import Course

    pct = get_attendance_percentage(db, student_id, course_id)
    if pct < threshold:
        course = db.query(Course).filter(Course.id == course_id).first()
        course_name = course.name if course else f"Course #{course_id}"
        # Avoid duplicate notifications: check if one already exists for same student/course
        existing = (
            db.query(Notification)
            .filter(
                Notification.user_id == student_id,
                Notification.notification_type == NotificationType.threshold_alert,
                Notification.title.like(f"%{course_name}%"),
                Notification.is_read == False,
            )
            .first()
        )
        if existing is None:
            create_notification(
                db,
                user_id=student_id,
                title=f"Low Attendance Alert: {course_name}",
                body=f"Your attendance in {course_name} has dropped to {pct:.1f}%, which is below the {threshold}% threshold.",
                notification_type=NotificationType.threshold_alert,
            )
