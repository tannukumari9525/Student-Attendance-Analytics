"""
Comprehensive seed script for local development and testing.
Creates: 2 departments, 4 courses, 4 teachers, 10 students, 1 parent,
         30 days of sessions per course, randomised attendance records.

Run from inside backend/:  python seed.py
"""
import sys
import os
import random
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
import models  # ensure all models are imported so Base.metadata is populated
from models.user import User, UserRole
from models.department import Department
from models.course import Course
from models.enrollment import Enrollment
from models.session import Session as CourseSession, SessionType
from models.attendance import AttendanceRecord, AttendanceStatus
from models.notification import Notification, NotificationType
from auth.password import hash_password

Base.metadata.create_all(bind=engine)

random.seed(42)


def get_or_create_dept(db, name: str, code: str) -> Department:
    d = db.query(Department).filter(Department.code == code).first()
    if not d:
        d = Department(name=name, code=code)
        db.add(d)
        db.flush()
        print(f"  Created department: {name} ({code})")
    else:
        print(f"  Department {code} already exists — skipping")
    return d


def get_or_create_user(db, name, email, password, role, dept_id=None, linked_student_id=None) -> User:
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            department_id=dept_id,
            linked_student_id=linked_student_id,
            is_active=True,
        )
        db.add(u)
        db.flush()
        print(f"  Created {role.value}: {email}")
    else:
        print(f"  {email} already exists — skipping")
    return u


def get_or_create_course(db, name, code, dept_id, teacher_id, credits, semester, year) -> Course:
    c = db.query(Course).filter(Course.code == code).first()
    if not c:
        c = Course(
            name=name,
            code=code,
            department_id=dept_id,
            teacher_id=teacher_id,
            credits=credits,
            semester=semester,
            academic_year=year,
            attendance_threshold=75.0,
        )
        db.add(c)
        db.flush()
        print(f"  Created course: {name} ({code})")
    else:
        print(f"  Course {code} already exists — skipping")
    return c


def ensure_enrollment(db, student_id, course_id):
    e = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id,
    ).first()
    if not e:
        e = Enrollment(student_id=student_id, course_id=course_id)
        db.add(e)
        db.flush()


def seed():
    db = SessionLocal()
    try:
        print("\n=== Seeding Departments ===")
        cs_dept = get_or_create_dept(db, "Computer Science", "CS")
        math_dept = get_or_create_dept(db, "Mathematics", "MATH")

        print("\n=== Seeding Admin ===")
        admin = get_or_create_user(db, "Demo Admin", "admin@demo.com", "admin123", UserRole.admin)

        print("\n=== Seeding Teachers ===")
        teachers = [
            get_or_create_user(db, f"Teacher {i}", f"teacher{i}@demo.com", "teacher123", UserRole.teacher, cs_dept.id)
            for i in range(1, 5)
        ]
        # Keep backward compat with teacher@demo.com
        get_or_create_user(db, "Demo Teacher", "teacher@demo.com", "teacher123", UserRole.teacher, cs_dept.id)

        print("\n=== Seeding Students ===")
        students = []
        for i in range(1, 11):
            s = get_or_create_user(
                db, f"Student {i:02d}", f"student{i:02d}@demo.com", "student123",
                UserRole.student, cs_dept.id,
            )
            students.append(s)
        # Keep backward compat
        get_or_create_user(db, "Demo Student", "student@demo.com", "student123", UserRole.student, cs_dept.id)

        print("\n=== Seeding Parent ===")
        parent = get_or_create_user(
            db, "Demo Parent", "parent@demo.com", "parent123",
            UserRole.parent, linked_student_id=students[0].id,
        )

        print("\n=== Seeding Courses ===")
        courses = [
            get_or_create_course(db, "Data Structures", "CS101", cs_dept.id, teachers[0].id, 4, "1", "2024-25"),
            get_or_create_course(db, "Operating Systems", "CS201", cs_dept.id, teachers[1].id, 4, "1", "2024-25"),
            get_or_create_course(db, "Database Management", "CS301", cs_dept.id, teachers[2].id, 3, "2", "2024-25"),
            get_or_create_course(db, "Discrete Mathematics", "MATH101", math_dept.id, teachers[3].id, 3, "1", "2024-25"),
        ]

        print("\n=== Enrolling Students ===")
        for student in students:
            for course in courses:
                ensure_enrollment(db, student.id, course.id)
        # Also enroll the demo student
        demo_student = db.query(User).filter(User.email == "student@demo.com").first()
        if demo_student:
            for course in courses:
                ensure_enrollment(db, demo_student.id, course.id)

        print("\n=== Seeding Sessions & Attendance (30 days each course) ===")
        today = date.today()
        start_date = today - timedelta(days=30)

        for course in courses:
            print(f"  Processing {course.code}…")
            teacher = db.query(User).filter(User.id == course.teacher_id).first()
            # Each weekday = 1 session
            d = start_date
            while d <= today:
                if d.weekday() < 5:  # Mon-Fri only
                    # Check if session already exists
                    existing_session = db.query(CourseSession).filter(
                        CourseSession.course_id == course.id,
                        CourseSession.date == d,
                    ).first()
                    if not existing_session:
                        session = CourseSession(
                            course_id=course.id,
                            date=d,
                            start_time=datetime.strptime("09:00", "%H:%M").time(),
                            end_time=datetime.strptime("10:00", "%H:%M").time(),
                            session_type=SessionType.lecture,
                            conducted_by=teacher.id,
                        )
                        db.add(session)
                        db.flush()
                    else:
                        session = existing_session

                    # Mark attendance for all enrolled students
                    enrolled_students = db.query(Enrollment).filter(
                        Enrollment.course_id == course.id
                    ).all()
                    for enroll in enrolled_students:
                        existing_record = db.query(AttendanceRecord).filter(
                            AttendanceRecord.session_id == session.id,
                            AttendanceRecord.student_id == enroll.student_id,
                        ).first()
                        if not existing_record:
                            # Randomise: 80% present, 10% absent, 5% late, 5% excused
                            rand = random.random()
                            if rand < 0.80:
                                status = AttendanceStatus.present
                            elif rand < 0.90:
                                status = AttendanceStatus.absent
                            elif rand < 0.95:
                                status = AttendanceStatus.late
                            else:
                                status = AttendanceStatus.excused
                            record = AttendanceRecord(
                                session_id=session.id,
                                student_id=enroll.student_id,
                                status=status,
                                marked_by=teacher.id,
                                marked_at=datetime.combine(d, datetime.strptime("10:00", "%H:%M").time()),
                            )
                            db.add(record)
                d += timedelta(days=1)

        db.commit()
        print("\nSeed complete.\n")
        print("Demo credentials:")
        print("  admin@demo.com       / admin123")
        print("  teacher@demo.com     / teacher123")
        print("  teacher1@demo.com    / teacher123")
        print("  student@demo.com     / student123")
        print("  student01@demo.com   / student123")
        print("  parent@demo.com      / parent123")

    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed()
