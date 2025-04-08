from fastapi.openapi.models import Schema
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    TRAINING = "Entrenamiento"
    RIDE = "Rodada"

class EventLevel(str, Enum):
    BASIC = "Básico"
    INTERMEDIATE = "Intermedio"
    ADVANCED = "Avanzado"
class EventBase(BaseModel):
    event_type: EventType
    route_id: int
    event_level: EventLevel
    image: Optional[HttpUrl] = None
    creation_date: datetime
    meeting_point: str
class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    event_type: Optional[EventType]=None
    route_id: Optional[int]=None
    event_level: Optional[EventLevel]=None
    image: Optional[HttpUrl]=None
    creation_date: Optional[datetime]=None
    meeting_point: Optional[str]=None

class EventResponse(EventBase):
    id: int
    class Config:
        from_attributes = True
