import base64
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.domain.event import Event
from app.models.schema.event import EventCreate, EventUpdate, EventResponse
from app.services.verify import verify_image_size


def create_event(db: Session, event_data: EventCreate) -> EventResponse:
    create_data = event_data.dict()

    if "image" in create_data and create_data["image"]:
        create_data["image"] = verify_image_size(create_data["image"])

    from datetime import datetime
    create_data["is_available"] = datetime.now() <= event_data.creation_date

    db_event = Event(**create_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return EventResponse.from_orm(db_event)

def get_events(db: Session):
    # 🔄 Actualiza en la base de datos los eventos ya pasados
    db.query(Event).filter(Event.creation_date < datetime.now(), Event.is_available == True).update(
        {Event.is_available: False}, synchronize_session=False
    )
    db.commit()

    # 🔁 Devuelve todos los eventos (con rutas)
    return db.query(Event).options(joinedload(Event.route)).order_by(Event.creation_date.desc()).all()

def update_event(db: Session, event_id: int, event_data: EventUpdate):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None

    update_data = event_data.dict(exclude_unset=True)

    if "image" in update_data and update_data["image"]:
        if isinstance(update_data["image"], str):
            # Si viene como string (data:image/png;base64,....)
            if update_data["image"].startswith("data:image"):
                base64_data = update_data["image"].split(",")[1]  # Remover el encabezado
            else:
                base64_data = update_data["image"]
            update_data["image"] = base64.b64decode(base64_data)

    for key, value in update_data.items():
        setattr(db_event, key, value)

    if "creation_date" in update_data:
        db_event.is_available = datetime.now() <= db_event.creation_date

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
