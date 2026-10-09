import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AttendanceRecordCreate(BaseModel):
    session_id: int
    student_id: int
    status: str  # present / absent / late / excused


class AttendanceBulkItem(BaseModel):
    student_id: int
    status: str


class AttendanceBulkCreate(BaseModel):
    session_id: int
    records: list[AttendanceBulkItem]


class AttendanceRecordUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class AttendanceRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    student_id: int
    status: str
    marked_by: int
    marked_at: datetime.datetime
    notes: Optional[str] = None
