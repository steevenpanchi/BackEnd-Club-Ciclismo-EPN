import base64

from fastapi.openapi.models import Schema
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum

from app.models.schema.route import RouteResponse


class EventType(str, Enum):
    TRAINING = "Entrenamiento"
    RIDE = "Rodada"

class EventLevel(str, Enum):
    BASIC = "Básico"
    INTERMEDIATE = "Intermedio"
    ADVANCED = "Avanzado"

class EventMode(str, Enum):
    MOUNTAIN = "Montaña"
    ROAD = "Carretera"

class EventBase(BaseModel):
    event_type: EventType
    route_id: int
    meeting_point: str
    creation_date: datetime
    event_level: EventLevel
    event_mode: EventMode
    image: Optional[str] = None
class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    event_type: Optional[EventType] = None
    route_id: Optional[int] = None
    meeting_point: Optional[str] = None
    creation_date: Optional[datetime] = None
    event_level: Optional[EventLevel] = None
    event_mode: Optional[EventMode] = None
    image: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    event_type: EventType
    route_id: int
    route_name: Optional[str]
    meeting_point: str
    creation_date: datetime
    event_level: EventLevel
    event_mode: EventMode
    is_available: bool
    image: Optional[str] = None

    class Config:
        from_attributes = True
        extra = "ignore"

    @classmethod
    def from_orm(cls, obj):
        image_base64 = None
        if obj.image and isinstance(obj.image, (bytes, bytearray)):
            try:
                image_base64 = f"data:image/png;base64,{base64.b64encode(obj.image).decode()}"
            except Exception:
                image_base64 = None

        return cls(
            id=obj.id,
            event_type=obj.event_type,
            route_id=obj.route_id,
            route_name=obj.route.name if hasattr(obj, 'route') and obj.route else None,
            meeting_point=obj.meeting_point,
            creation_date=obj.creation_date,
            event_level=obj.event_level,
            event_mode=obj.event_mode,
            is_available=obj.is_available,
            image=image_base64
        )

class NextEventPublicResponse(BaseModel):
    id: int
    event_type: EventType
    creation_date: datetime
    event_level: EventLevel
    event_mode: EventMode
    is_available: bool
    route: RouteResponse
    image: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        def get_default_image():
            try:
                with open("app/static/default_event.jpg", "rb") as f:
                    return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
            except Exception as e:
                print(f"Error cargando imagen por defecto: {e}")
                return None

        # Imagen base64
        image_base64 = None
        if obj.image and isinstance(obj.image, (bytes, bytearray)):
            try:
                image_base64 = f"data:image/png;base64,{base64.b64encode(obj.image).decode()}"
            except Exception:
                image_base64 = get_default_image()
        elif not obj.image or str(obj.image).strip().lower() == "string":
            image_base64 = get_default_image()
        else:
            image_base64 = obj.image  # ya viene como base64

        # RouteResponse correctamente construido
        route_data = RouteResponse(
            id=obj.route.id,
            name=obj.route.name,
            start_point=obj.route.start_point,
            end_point=obj.route.end_point,
            duration=obj.route.duration
        ) if obj.route else None

        return cls(
            id=obj.id,
            event_type=obj.event_type,
            creation_date=obj.creation_date,
            event_level=obj.event_level,
            event_mode=obj.event_mode,
            is_available=obj.is_available,
            image=image_base64,
            route=route_data
        )
