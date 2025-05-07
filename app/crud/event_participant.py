import pytz
from sqlalchemy.orm import Session, selectinload
from app.models.domain.event_participant import EventParticipant
from app.models.domain.user import User
from app.models.schema.event_participant import EventParticipantCreate
from datetime import datetime


def create_participation(db: Session, user_id: int, participation: EventParticipantCreate):
    ecuador = pytz.timezone('America/Guayaquil')
    now_local = datetime.now(ecuador)

    new_part = EventParticipant(
        user_id=user_id,
        event_id=participation.event_id,
        registered_at=now_local
    )
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return new_part
def get_participants_by_event(db: Session, event_id: int):
    return (
        db.query(EventParticipant)
        .options(
            selectinload(EventParticipant.user).selectinload(User.person)
        )
        .filter(EventParticipant.event_id == event_id)
        .all()
    )

def delete_participation(db: Session, user_id: int, event_id: int):
    participation = (
        db.query(EventParticipant)
        .filter(
            EventParticipant.user_id == user_id,
            EventParticipant.event_id == event_id
        )
        .first()
    )

    if not participation:
        return None

    db.delete(participation)
    db.commit()
    return participation
