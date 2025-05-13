from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, DateTime, LargeBinary, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


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


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(SQLAEnum(EventType), nullable=False)
    route_id = Column(Integer, ForeignKey("route.id", ondelete="CASCADE"), nullable=False)
    meeting_point = Column(String(255), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    event_level = Column(SQLAEnum(EventLevel), nullable=False)
    event_mode = Column(SQLAEnum(EventMode), nullable=False)
    is_available = Column(Boolean, default=True)
    image = Column(LargeBinary, nullable=True)

    # Relación con Route
    route = relationship("Route", back_populates="events")

    # Relación con EventParticipant
    participants = relationship("EventParticipant", back_populates="event", cascade="all, delete")
