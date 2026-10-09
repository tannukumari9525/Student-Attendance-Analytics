import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    course_id: int
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    session_type: str  # lecture / lab / seminar / tutorial


class SessionUpdate(BaseModel):
    date: Optional[datetime.date] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    session_type: Optional[str] = None


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    session_type: str
    conducted_by: int
