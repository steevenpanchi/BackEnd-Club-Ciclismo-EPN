import base64
import locale
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.crud.notification import create_notification
from app.models.domain.event import Event
from app.models.domain.event_participant import EventParticipant
from app.models.domain.user import User
from app.models.schema.event import EventCreate, EventUpdate, EventResponse
from app.services.verify import verify_image_size

locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

def create_event(db: Session, event_data: EventCreate) -> EventResponse:
    create_data = event_data.dict()

    if "image" in create_data and create_data["image"]:
        create_data["image"] = verify_image_size(create_data["image"])

    create_data["is_available"] = datetime.now() <= event_data.creation_date

    db_event = Event(**create_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    db_event = (
        db.query(Event)
        .options(joinedload(Event.route))
        .filter(Event.id == db_event.id)
        .first()
    )

    dia_semana = db_event.creation_date.strftime("%A").capitalize()
    resto_fecha = db_event.creation_date.strftime("%d de %B del %Y")
    fecha_formateada = f"{dia_semana} {resto_fecha}"

    nombre_ruta = db_event.route.name if db_event.route else "Ruta sin nombre"

    normal_users = db.query(User).filter(User.role == "Normal").all()
    for user in normal_users:
        create_notification(
            db,
            user_id=user.id,
            title="¡Nuevo evento disponible!",
            message=f"Se ha creado el evento {db_event.event_type.value} {nombre_ruta} para el día {fecha_formateada}. ¡Inscríbete ahora!"
        )

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

    db_event = (
        db.query(Event)
        .options(joinedload(Event.route))
        .filter(Event.id == event_id)
        .first()
    )

    dia_semana = db_event.creation_date.strftime("%A").capitalize()
    resto_fecha = db_event.creation_date.strftime("%d de %B del %Y")
    fecha_formateada = f"{dia_semana} {resto_fecha}"

    inscritos = db.query(EventParticipant).filter(EventParticipant.event_id == event_id).all()
    nombre_ruta = db_event.route.name if db_event.route else "Ruta sin nombre"

    for ins in inscritos:
        create_notification(
            db,
            user_id=ins.user_id,
            title="Evento actualizado",
            message=f"El evento {db_event.event_type.value} {nombre_ruta} del día {fecha_formateada} ha sido actualizado. Revisa los nuevos detalles en la plataforma."
        )

    return db_event



def delete_event(db: Session, event_id: int):
    db_event = (
        db.query(Event)
        .options(joinedload(Event.route))
        .filter(Event.id == event_id)
        .first()
    )
    if not db_event:
        return None


    dia_semana = db_event.creation_date.strftime("%A").capitalize()
    resto_fecha = db_event.creation_date.strftime("%d de %B del %Y")
    fecha_formateada = f"{dia_semana} {resto_fecha}"

    inscritos = db.query(EventParticipant).filter(EventParticipant.event_id == event_id).all()
    nombre_ruta = db_event.route.name if db_event.route else "Ruta sin nombre"

    for ins in inscritos:
        create_notification(
            db,
            user_id=ins.user_id,
            title="Evento cancelado",
            message=f'El evento "{db_event.event_type.value} {nombre_ruta}" del día {fecha_formateada} ha sido cancelado. Lamentamos los inconvenientes.'
        )

    db.delete(db_event)
    db.commit()
    return db_event