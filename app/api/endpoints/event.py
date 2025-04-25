from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.domain.user import Role
from app.models.schema.event import EventCreate, EventResponse, EventUpdate
from app.crud.event import create_event, get_events, update_event, delete_event, get_event_by_id
from app.models.schema.user import TokenData

router = APIRouter()
ALL_AUTH_ROLES = [Role.ADMIN, Role.NORMAL]
@router.post("/create", response_model=EventResponse)
def create_new_event(event: EventCreate, db: Session = Depends(get_db),
                     current_user: TokenData = Depends(get_current_user)):
    """
     Create a New Event / Crear un Nuevo Evento

     English:
     --------
     Register a new cycling event.

     - **event_type** (required): Type of the event (e.g., Training, Race).
     - **route_id** (required): Route associated with the event.
     - **meeting_point** (required): Location where the event will meet.
     - **creation_date** (required): Date and time when the event is created.
     - **event_level** (required): Level of the event (e.g., Basic, Intermediate, Advanced).
     - **event_mode** (required): Event modality (e.g., Mountain, Road).
     - **image** (optional): Image of the event.

     Español:
     --------
     Registrar un nuevo evento de ciclismo.

     - **event_type** (requerido): Tipo del evento (por ejemplo, Entrenamiento, Rodada).
     - **route_id** (requerido): Ruta asociada al evento.
     - **meeting_point** (requerido): Lugar donde se llevará a cabo el evento.
     - **creation_date** (requerido): Fecha y hora en que se crea el evento.
     - **event_level** (requerido): Nivel del evento (por ejemplo, Básico, Intermedio, Avanzado).
     - **event_mode** (requerido): Modalidad del evento (por ejemplo, Montaña, Carretera).
     - **image** (opcional): Imagen del evento.

     """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        return create_event(db, event)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Validación fallida: {str(ve)}")
    except Exception as e:
        print(f"Error interno en crear evento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/", response_model=List[EventResponse])
def read_all_events(db: Session = Depends(get_db),
                    current_user: TokenData = Depends(get_current_user)):
    """
      Get all registered events with their details.

      English:
      --------
      Returns a list of all registered events, including their type, associated route, event level, image, and creation date.

      Español:
      --------
      Devuelve una lista de todos los eventos registrados, incluyendo su tipo, ruta asociada, nivel del evento, imagen y fecha de creación.
      """
    if current_user.role.value not in ALL_AUTH_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return get_events(db)

@router.get("/{event_id}", response_model=EventResponse)
def read_event(event_id: int, db: Session = Depends(get_db),
               current_user: TokenData = Depends(get_current_user)
               ):
    """
    Get Event by ID / Obtener evento por ID

    English:
    --------
    Retrieve a cycling event by its ID.

    - **event_id** (required): ID of the event to retrieve.

    Español:
    --------
    Obtener un evento de ciclismo por su ID.

    - **event_id** (requerido): ID del evento a obtener.
    """
    if current_user.role.value not in ALL_AUTH_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return get_events(db)

    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/update/{event_id}", response_model=EventResponse)
def modify_event(event_id: int, event_data: EventUpdate, db: Session = Depends(get_db),
                 current_user: TokenData = Depends(get_current_user)
                 ):
    """
    Update event details by its ID.

    English:
    --------
    Update the details of an event by its ID.

     - **event_type** (optional): Type of the event (e.g., Training, Race).
     - **route_id** (optional): Route associated with the event.
     - **meeting_point** (optional): Location where the event will meet.
     - **creation_date** (optional): Date and time when the event is created.
     - **event_level** (optional): Level of the event (e.g., Basic, Intermediate, Advanced).
     - **event_mode** (optional): Event modality (e.g., Mountain, Road).
     - **image** (optional): Image ode the event.


    Español:
    --------
    Actualiza los detalles de un evento mediante su ID.

     - **event_type** (opcional): Tipo del evento (por ejemplo, Entrenamiento, Rodada).
     - **route_id** (opcional): Ruta asociada al evento.
     - **meeting_point** (opcional): Lugar donde se llevará a cabo el evento.
     - **creation_date** (opcional): Fecha y hora en que se crea el evento.
     - **event_level** (opcional): Nivel del evento (por ejemplo, Básico, Intermedio, Avanzado).
     - **event_mode** (opcional): Modalidad del evento (e.g., Montaña, Carretera).
     - **image** (opcional): Imagen del evento.

    """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_event = update_event(db, event_id, event_data)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@router.delete("/delete/{event_id}", response_model=dict)
def remove_event(event_id: int, db: Session = Depends(get_db),
                 current_user: TokenData = Depends(get_current_user)
                 ):
    """
      Delete event by ID / Eliminar evento por ID

      English:
      --------
      Delete a cycling event by its ID.

      - **event_id** (required): ID of the event to delete.

      Español:
      --------
      Eliminar un evento de ciclismo por su ID.

      - **event_id** (requerido): ID del evento a eliminar.
      """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if not delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}
