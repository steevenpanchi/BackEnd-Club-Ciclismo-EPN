from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, DateTime
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


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(SQLAEnum(EventType), nullable=False)
    route_id = Column(Integer, ForeignKey("route.id", ondelete="CASCADE"), nullable=False)
    event_level = Column(SQLAEnum(EventLevel), nullable=False)
    image = Column(String(255), nullable=True)
    creation_date = Column(DateTime, default=datetime.utcnow)
    meeting_point = Column(String(255), nullable=False)


    # Relationship with Route
    route = relationship("Route", back_populates="events")
