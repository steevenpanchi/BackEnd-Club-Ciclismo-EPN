from sqlalchemy.orm import Session
from app.models.domain.event import Event
from app.models.schema.event import EventCreate, EventUpdate, EventResponse
from app.services.verify import verify_image_size


def create_event(db: Session, event_data: EventCreate) -> EventResponse:


    create_data = event_data.dict()

    # Si se envía imagen base64, convertirla a bytes y validar
    if "image" in create_data and create_data["image"]:
        create_data["image"] = verify_image_size(create_data["image"])

    db_event = Event(**create_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Devolver el evento usando el método from_orm para transformar la imagen
    return EventResponse.from_orm(db_event)


def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def get_events(db: Session):
    return db.query(Event).order_by(Event.creation_date.desc()).all()


def update_event(db: Session, event_id: int, event_data: EventUpdate):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None

    update_data = event_data.dict(exclude_unset=True)

    # Procesar imagen base64 si se envía
    if "image" in update_data and update_data["image"]:
        update_data["image"] = verify_image_size(update_data["image"])

    for key, value in update_data.items():
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
