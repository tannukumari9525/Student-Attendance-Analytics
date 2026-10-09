"""
Analytics service: aggregation queries.
"""
from sqlalchemy import func, text
from sqlalchemy.orm import Session as DBSession

from models.attendance import AttendanceRecord, AttendanceStatus
from models.course import Course
from models.enrollment import Enrollment
from models.session import Session as SessionModel
from models.user import User, UserRole


def student_course_stats(db: DBSession, student_id: int) -> list[dict]:
    """Per-course attendance % for a student."""
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    result = []
    for e in enrollments:
        total = db.query(SessionModel).filter(SessionModel.course_id == e.course_id).count()
        if total == 0:
            pct = 0.0
        else:
            attended = (
                db.query(AttendanceRecord)
                .join(SessionModel, AttendanceRecord.session_id == SessionModel.id)
                .filter(
                    AttendanceRecord.student_id == student_id,
                    SessionModel.course_id == e.course_id,
                    AttendanceRecord.status.in_([AttendanceStatus.present, AttendanceStatus.late]),
                )
                .count()
            )
            pct = round(attended / total * 100, 2)
        course = db.query(Course).filter(Course.id == e.course_id).first()
        result.append(
            {
                "course_id": e.course_id,
                "course_name": course.name if course else "",
                "course_code": course.code if course else "",
                "total_sessions": total,
                "attendance_percentage": pct,
                "threshold": course.attendance_threshold if course else 75.0,
            }
        )
    return result


def course_weekly_trend(db: DBSession, course_id: int) -> list[dict]:
    """Weekly attendance % trend for a course."""
    rows = db.execute(
        text(
            """
            SELECT strftime('%Y-%W', s.date) AS week,
                   COUNT(DISTINCT s.id) AS total_sessions,
                   COUNT(CASE WHEN ar.status IN ('present', 'late') THEN 1 END) AS attended,
                   COUNT(ar.id) AS total_records
            FROM sessions s
            LEFT JOIN attendance_records ar ON ar.session_id = s.id
            WHERE s.course_id = :course_id
            GROUP BY week
            ORDER BY week
            """
        ),
        {"course_id": course_id},
    ).fetchall()
    result = []
    for row in rows:
        total_records = row[3] or 0
        attended = row[2] or 0
        pct = round(attended / total_records * 100, 2) if total_records > 0 else 0.0
        result.append({"week": row[0], "attendance_percentage": pct, "total_sessions": row[1]})
    return result


def course_heatmap(db: DBSession, course_id: int) -> list[dict]:
    """Daily attendance data for calendar heatmap."""
    rows = db.execute(
        text(
            """
            SELECT s.date, ar.status, COUNT(ar.id) AS count
            FROM sessions s
            LEFT JOIN attendance_records ar ON ar.session_id = s.id
            WHERE s.course_id = :course_id
            GROUP BY s.date, ar.status
            ORDER BY s.date
            """
        ),
        {"course_id": course_id},
    ).fetchall()
    return [{"date": str(row[0]), "status": row[1], "count": row[2]} for row in rows]


def course_day_of_week(db: DBSession, course_id: int) -> list[dict]:
    """Average attendance % per day of week."""
    rows = db.execute(
        text(
            """
            SELECT strftime('%w', s.date) AS dow,
                   COUNT(CASE WHEN ar.status IN ('present', 'late') THEN 1 END) AS attended,
                   COUNT(ar.id) AS total
            FROM sessions s
            LEFT JOIN attendance_records ar ON ar.session_id = s.id
            WHERE s.course_id = :course_id
            GROUP BY dow
            ORDER BY dow
            """
        ),
        {"course_id": course_id},
    ).fetchall()
    dow_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    result = []
    for row in rows:
        pct = round(row[1] / row[2] * 100, 2) if row[2] > 0 else 0.0
        result.append({"day": dow_names[int(row[0])], "attendance_percentage": pct})
    return result


def course_student_ranking(db: DBSession, course_id: int) -> list[dict]:
    """Per-student attendance % ranked for a course."""
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    total = db.query(SessionModel).filter(SessionModel.course_id == course_id).count()
    result = []
    for e in enrollments:
        if total == 0:
            pct = 0.0
        else:
            attended = (
                db.query(AttendanceRecord)
                .join(SessionModel, AttendanceRecord.session_id == SessionModel.id)
                .filter(
                    AttendanceRecord.student_id == e.student_id,
                    SessionModel.course_id == course_id,
                    AttendanceRecord.status.in_([AttendanceStatus.present, AttendanceStatus.late]),
                )
                .count()
            )
            pct = round(attended / total * 100, 2)
        result.append(
            {
                "student_id": e.student_id,
                "student_name": e.student.name,
                "attendance_percentage": pct,
            }
        )
    result.sort(key=lambda x: x["attendance_percentage"], reverse=True)
    return result


def admin_summary(db: DBSession) -> dict:
    total_students = db.query(User).filter(User.role == UserRole.student).count()
    total_teachers = db.query(User).filter(User.role == UserRole.teacher).count()
    total_courses = db.query(Course).count()
    total_sessions_today = (
        db.execute(
            text("SELECT COUNT(*) FROM sessions WHERE date = date('now')")
        ).scalar()
        or 0
    )
    # Defaulters across all courses (below 75%)
    # We compute this lazily: count distinct students with pct < 75 in any course
    all_enrollments = db.query(Enrollment).all()
    defaulter_set = set()
    for e in all_enrollments:
        total = db.query(SessionModel).filter(SessionModel.course_id == e.course_id).count()
        if total == 0:
            continue
        attended = (
            db.query(AttendanceRecord)
            .join(SessionModel, AttendanceRecord.session_id == SessionModel.id)
            .filter(
                AttendanceRecord.student_id == e.student_id,
                SessionModel.course_id == e.course_id,
                AttendanceRecord.status.in_([AttendanceStatus.present, AttendanceStatus.late]),
            )
            .count()
        )
        if attended / total * 100 < 75:
            defaulter_set.add(e.student_id)
    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_courses": total_courses,
        "sessions_today": total_sessions_today,
        "defaulter_count": len(defaulter_set),
    }


def teacher_summary(db: DBSession, teacher_id: int) -> dict:
    courses = db.query(Course).filter(Course.teacher_id == teacher_id).all()
    course_stats = []
    defaulter_total = 0
    for course in courses:
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
        total = db.query(SessionModel).filter(SessionModel.course_id == course.id).count()
        defaulters = 0
        for e in enrollments:
            if total == 0:
                continue
            attended = (
                db.query(AttendanceRecord)
                .join(SessionModel, AttendanceRecord.session_id == SessionModel.id)
                .filter(
                    AttendanceRecord.student_id == e.student_id,
                    SessionModel.course_id == course.id,
                    AttendanceRecord.status.in_([AttendanceStatus.present, AttendanceStatus.late]),
                )
                .count()
            )
            if attended / total * 100 < course.attendance_threshold:
                defaulters += 1
        defaulter_total += defaulters
        course_stats.append(
            {
                "course_id": course.id,
                "course_name": course.name,
                "course_code": course.code,
                "student_count": len(enrollments),
                "total_sessions": total,
                "defaulter_count": defaulters,
            }
        )
    return {"courses": course_stats, "total_defaulters": defaulter_total}
