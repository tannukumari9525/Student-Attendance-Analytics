from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models.notification import Notification
from models.user import User
from schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _to_read(n: Notification) -> NotificationRead:
    return NotificationRead(
        id=n.id,
        user_id=n.user_id,
        title=n.title,
        body=n.body,
        is_read=n.is_read,
        created_at=n.created_at,
        notification_type=n.notification_type.value if hasattr(n.notification_type, "value") else n.notification_type,
    )


@router.get("/", response_model=list[NotificationRead])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [_to_read(n) for n in notifications]


@router.patch("/{notif_id}/read", response_model=NotificationRead)
def mark_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    n = (
        db.query(Notification)
        .filter(Notification.id == notif_id, Notification.user_id == current_user.id)
        .first()
    )
    if not n:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    db.refresh(n)
    return _to_read(n)


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
