from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud import event_participant as crud_part
from app.db.session import get_db
from app.models.domain.event import Event
from app.models.domain.event_participant import EventParticipant
from app.models.domain.user import User, Role
from app.models.schema.event_participant import EventParticipantCreate, ParticipantsResponse
from app.models.schema.persona import PersonaResponse
from app.models.schema.user import UserBasicResponse

router = APIRouter()
ALL_AUTH_ROLES = [Role.ADMIN, Role.NORMAL]


@router.post("/register_event")
def register_user_to_event(
        participation: EventParticipantCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Register User to Event / Inscribir Usuario a un Evento

    English:
    --------
    Allows a user with role 'Normal' to register for a cycling event.

    - **Requires authentication.**
    - **Only users with role 'Normal' can register.**
    - Returns an error if the user is already registered.
    - **event_id** (required): ID of the event to register.

    Español:
    --------
    Permite que un usuario con rol 'Normal' se inscriba en un evento de ciclismo.

    - **Requiere autenticación.**
    - **Solo los usuarios con rol 'Normal' pueden registrarse.**
    - Devuelve error si el usuario ya está inscrito.
    - **event_id** (requerido): ID del evento al que se desea registrar.

    """
    if current_user.role != Role.NORMAL:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    existing = (
        db.query(EventParticipant)
        .filter(EventParticipant.user_id == current_user.id)
        .filter(EventParticipant.event_id == participation.event_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Ya estás inscrito en este evento")

    crud_part.create_participation(db, user_id=current_user.id, participation=participation)

    return {"detail": "Te has inscrito correctamente en el evento"}


@router.get("/event/{event_id}", response_model=List[ParticipantsResponse])
def get_participants(event_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):

    """
    Get Event Participants / Obtener Participantes del Evento

    English:
    --------
    Retrieve the list of users registered for a specific event.
    - **Only accessible by users with the 'Admin' role.**
    - Returns participant information including user and personal details.
    - **event_id** (int): ID of the event to retrieve participants for.

    Español:
    --------
    Obtiene la lista de usuarios inscritos en un evento específico.
    - **Solo accesible para usuarios con rol 'Admin'.**
    - Devuelve información del participante, incluyendo detalles del usuario y su persona asociada.
    - **event_id** (int): ID del evento del cual se desea obtener los participantes.


    """
    if current_user.role.value not in Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    participants = (
        db.query(EventParticipant)
        .join(EventParticipant.user)
        .join(User.person)
        .filter(EventParticipant.event_id == event_id)
        .all()
    )
    response = []
    for p in participants:
        response.append(
            ParticipantsResponse(
                id=p.id,
                event_id=p.event_id,
                registered_at=p.registered_at,
                user=UserBasicResponse(
                    id=p.user.id,
                    email=p.user.email,
                    person=PersonaResponse.from_orm(p.user.person)
                )
            )
        )

    return response


@router.delete("/unregister_event/{event_id}")
def unregister_user_from_event(
        event_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Unregister from Event / Cancelar Inscripción en un Evento

    English:
    --------
    Allows a user with role 'Normal' to cancel their registration for a cycling event.

    - **Requires authentication.**
    - **Only users with role 'Normal' can unregister.**
    - Returns an error if the user is not enrolled or the event does not exist.
    - **event_id** (int): ID of the event to unregister from.

    Español:
    --------
    Permite que un usuario con rol 'Normal' cancele su inscripción en un evento de ciclismo.

    - **Requiere autenticación.**
    - **Solo los usuarios con rol 'Normal' pueden cancelar su inscripción.**
    - Devuelve error si el evento no existe o el usuario no está inscrito.
    - **event_id** (int): ID del evento del cual se desea cancelar la inscripción.

    """

    if current_user.role != Role.NORMAL:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Verificar que el evento existe
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="El evento no existe")

    # Eliminar participación
    deleted = crud_part.delete_participation(db, user_id=current_user.id, event_id=event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No estás inscrito en este evento")

    return {"detail": "Te has desenrolado del evento correctamente"}
