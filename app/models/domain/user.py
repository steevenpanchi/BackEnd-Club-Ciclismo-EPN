from enum import Enum

from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Role(str, Enum):
    ADMIN = "Admin"
    NORMAL = "Normal"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # Obligatorio
    role = Column(SQLAEnum(Role), nullable=False)
    person_id = Column(Integer, ForeignKey("persona.id", ondelete="CASCADE"), nullable=False)

    # Relación con Persona
    person = relationship("Persona", back_populates="user", uselist=False)

    # Relación con AuthToken
    token = relationship("AuthToken", uselist=False, back_populates="user")

    # Relación con EventParticipant
    event_participations = relationship("EventParticipant", back_populates="user", cascade="all, delete")

    # Relación con User
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
