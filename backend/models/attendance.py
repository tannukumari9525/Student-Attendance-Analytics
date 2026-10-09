import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class AttendanceStatus(enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"
    excused = "excused"


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    marked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String, nullable=True)

    # Relationships
    session = relationship("Session", back_populates="attendance_records")
    student = relationship("User", back_populates="attendance_records", foreign_keys=[student_id])
    marker = relationship("User", back_populates="marked_attendance", foreign_keys=[marked_by])
