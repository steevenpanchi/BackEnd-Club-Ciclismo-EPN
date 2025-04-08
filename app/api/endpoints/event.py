from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.schema.event import EventCreate, EventResponse, EventUpdate
from app.crud.event import create_event, get_events, update_event, delete_event, get_event_by_id

router = APIRouter()

@router.post("/create", response_model=EventResponse)
def create_new_event(event: EventCreate, db: Session = Depends(get_db)):
    """
     Create a New Event / Crear un Nuevo Evento

     English:
     --------
     Register a new cycling event.

     - **event_type** (required): Type of the event (e.g., Training, Race).
     - **route_id** (required): ID of the route associated with the event.
     - **event_level** (required): Level of the event (e.g., Basic, Intermediate, Advanced).
     - **image** (required): URL for the event's image.
     - **creation_date** (required): Date and time when the event is created.
     - **meeting_point** (required): Location where the event will meet.

     Español:
     --------
     Registrar un nuevo evento de ciclismo.

     - **event_type** (requerido): Tipo del evento (por ejemplo, Entrenamiento, Carrera).
     - **route_id** (requerido): ID de la ruta asociada al evento.
     - **event_level** (requerido): Nivel del evento (por ejemplo, Básico, Intermedio, Avanzado).
     - **image** (requerido): URL de la imagen del evento.
     - **creation_date** (requerido): Fecha y hora en que se crea el evento.
     - **meeting_point** (requerido): Lugar donde se llevará a cabo el evento.

     """
    return create_event(db, event)

@router.get("/", response_model=List[EventResponse])
def read_all_events(db: Session = Depends(get_db)):
    """
      Get all registered events with their details.

      English:
      --------
      Returns a list of all registered events, including their type, associated route, event level, image, and creation date.

      Español:
      --------
      Devuelve una lista de todos los eventos registrados, incluyendo su tipo, ruta asociada, nivel del evento, imagen y fecha de creación.
      """
    return get_events(db)

@router.get("/{event_id}", response_model=EventResponse)
def read_event(event_id: int, db: Session = Depends(get_db)):
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
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/update/{event_id}", response_model=EventResponse)
def modify_event(event_id: int, event_data: EventUpdate, db: Session = Depends(get_db)):
    """
    Update event details by its ID.

    English:
    --------
    Update the details of an event by its ID.

    - **event_type** (optional): Type of the event.
    - **route_id** (optional): ID of the associated route.
    - **event_level** (optional): Level of the event (e.g., Basic, Advanced).
    - **image** (optional): URL of the event image.
    - **creation_date** (optional): Date and time when the event was created.
    - **meeting_point** (required): Location where the event will meet.


    Español:
    --------
    Actualiza los detalles de un evento mediante su ID.

    - **event_type** (opcional): Tipo de evento.
    - **route_id** (opcional): ID de la ruta asociada.
    - **event_level** (opcional): Nivel del evento (por ejemplo, Básico, Avanzado).
    - **image** (opcional): URL de la imagen del evento.
    - **creation_date** (opcional): Fecha y hora en que se creó el evento.
    - **meeting_point** (requerido): Lugar donde se llevará a cabo el evento.

    """
    updated_event = update_event(db, event_id, event_data)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@router.delete("/delete/{event_id}", response_model=dict)
def remove_event(event_id: int, db: Session = Depends(get_db)):
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
    if not delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}
