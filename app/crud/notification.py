from sqlalchemy.orm import Session
from sqlalchemy import desc
import pytz
from datetime import datetime

from app.models.domain.notification import Notification
from app.models.schema.notification import NotificationResponse


def create_notification(db: Session, user_id: int, title: str, message: str) -> Notification:
    ecuador = pytz.timezone('America/Guayaquil')
    now_local = datetime.now(ecuador)
    noti = Notification(
        user_id=user_id,
        title=title,
        message=message,
        created_at=now_local
    )
    db.add(noti)
    db.commit()
    db.refresh(noti)
    return noti


def get_user_notifications(db: Session, user_id: int):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(desc(Notification.created_at))
        .all()
    )


def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    noti = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .filter(Notification.user_id == user_id)
        .first()
    )
    if not noti:
        return None

    noti.is_read = True
    db.commit()
    db.refresh(noti)
    return noti
