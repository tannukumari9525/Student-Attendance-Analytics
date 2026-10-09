import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    body: str
    is_read: bool
    created_at: datetime.datetime
    notification_type: str
