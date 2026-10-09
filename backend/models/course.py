from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    credits = Column(Integer, nullable=False)
    semester = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    attendance_threshold = Column(Float, default=75.0, nullable=False)

    # Relationships
    department = relationship("Department", back_populates="courses")
    teacher = relationship("User", back_populates="taught_courses", foreign_keys=[teacher_id])
    enrollments = relationship("Enrollment", back_populates="course")
    sessions = relationship("Session", back_populates="course")
    leave_requests = relationship("LeaveRequest", back_populates="course")
