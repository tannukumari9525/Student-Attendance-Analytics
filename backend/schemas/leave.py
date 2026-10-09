import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LeaveRequestCreate(BaseModel):
    course_id: int
    from_date: datetime.date
    to_date: datetime.date
    reason: str


class LeaveRequestReview(BaseModel):
    status: str  # approved / rejected


class LeaveRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    from_date: datetime.date
    to_date: datetime.date
    reason: str
    status: str
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
