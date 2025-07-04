from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud.notification import get_user_notifications, mark_notification_as_read
from app.db.session import get_db
from app.models.domain.user import User
from app.models.schema.notification import NotificationResponse

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_notifications(db, current_user.id)


@router.patch("/mark_as_read/{notification_id}", response_model=NotificationResponse)
def mark_as_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    noti = mark_notification_as_read(db, notification_id, current_user.id)
    if not noti:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return noti
