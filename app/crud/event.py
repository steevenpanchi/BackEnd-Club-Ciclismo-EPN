from sqlalchemy.orm import Session
from app.models.domain.event import Event
from app.models.schema.event import EventCreate, EventUpdate

def create_event(db: Session, event_data: EventCreate):
    db_event = Event(**event_data.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def get_events(db: Session):
    return db.query(Event).order_by(Event.creation_date.desc()).all()


def update_event(db: Session, event_id: int, event_data: EventUpdate):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    db.delete(db_event)
    db.commit()
    return db_event
