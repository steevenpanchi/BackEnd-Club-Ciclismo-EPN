from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base

class Route(Base):
    __tablename__ = "route"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    start_point = Column(String(255), nullable=False)
    end_point = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=False)

    # Relationship with Event
    events = relationship("Event", back_populates="route")
