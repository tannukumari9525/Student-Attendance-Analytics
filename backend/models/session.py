import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship

from database import Base


class SessionType(enum.Enum):
    lecture = "lecture"
    lab = "lab"
    seminar = "seminar"
    tutorial = "tutorial"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    session_type = Column(Enum(SessionType), nullable=False)
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    course = relationship("Course", back_populates="sessions")
    conductor = relationship("User", back_populates="conducted_sessions", foreign_keys=[conducted_by])
    attendance_records = relationship("AttendanceRecord", back_populates="session")
