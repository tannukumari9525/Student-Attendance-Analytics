import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class UserRole(enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    parent = "parent"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    linked_student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department = relationship("Department", back_populates="users")
    linked_student = relationship("User", remote_side=[id], foreign_keys=[linked_student_id])

    # Courses this user teaches
    taught_courses = relationship("Course", back_populates="teacher", foreign_keys="Course.teacher_id")

    # Sessions conducted by this user
    conducted_sessions = relationship("Session", back_populates="conductor", foreign_keys="Session.conducted_by")

    # Enrollments (student role)
    enrollments = relationship("Enrollment", back_populates="student", foreign_keys="Enrollment.student_id")

    # Attendance records as student
    attendance_records = relationship("AttendanceRecord", back_populates="student", foreign_keys="AttendanceRecord.student_id")

    # Attendance records marked by this user
    marked_attendance = relationship("AttendanceRecord", back_populates="marker", foreign_keys="AttendanceRecord.marked_by")

    # Leave requests (student)
    leave_requests = relationship("LeaveRequest", back_populates="student", foreign_keys="LeaveRequest.student_id")

    # Leave requests reviewed by this user
    reviewed_leaves = relationship("LeaveRequest", back_populates="reviewer", foreign_keys="LeaveRequest.reviewed_by")

    # Notifications
    notifications = relationship("Notification", back_populates="user")
