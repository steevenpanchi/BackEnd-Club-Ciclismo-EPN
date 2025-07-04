import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.models.domain.event import Event
from app.models.domain.event_participant import EventParticipant
from app.models.domain.user import User
from app.models.domain.notification import Notification  # Importación agregada
from app.crud.notification import create_notification

def notificar_eventos_24h():
    db: Session = SessionLocal()
    try:
        ecuador = pytz.timezone('America/Guayaquil')
        ahora = datetime.now(ecuador)
        print(f"🔔 [Scheduler] Buscando eventos para: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")

        objetivo = ahora + timedelta(hours=24)
        inicio_rango = objetivo.replace(second=0, microsecond=0)
        fin_rango = inicio_rango + timedelta(minutes=1)

        eventos_proximos = db.query(Event).options(joinedload(Event.route)).filter(
            Event.creation_date >= inicio_rango,
            Event.creation_date < fin_rango
        ).all()

        print(f"🔎 Se encontraron {len(eventos_proximos)} eventos próximos")

        for evento in eventos_proximos:
            participantes = db.query(EventParticipant).filter(
                EventParticipant.event_id == evento.id
            ).all()

            for part in participantes:
                user = db.query(User).filter(User.id == part.user_id).first()
                if user:
                    titulo = f"¡Recordatorio de evento!"

                    # Evitar notificación duplicada
                    ya_existe = db.query(Notification).filter(
                        Notification.user_id == user.id,
                        Notification.title == titulo
                    ).first()

                    if not ya_existe:
                        create_notification(
                            db,
                            user_id=user.id,
                            title=titulo,
                            message=f"Recuerda que el evento {evento.event_type.value} {evento.route.name} es mañana a las {evento.creation_date.strftime('%H:%M')}. ¡Prepárate!"
                        )
                    else:
                        print(f"Notificación ya existente para usuario {user.id} y evento {evento.id}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(notificar_eventos_24h, "interval", minutes=1)
    scheduler.start()
