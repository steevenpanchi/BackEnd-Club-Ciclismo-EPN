from enum import Enum

from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, LargeBinary
from sqlalchemy.orm import relationship
from app.db.database import Base

class SkillLevel(str, Enum):
    LOW = "Bajo"
    MEDIUM = "Medio"
    HIGH = "Alto"

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class Persona(Base):
    __tablename__ = "persona"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone_number = Column(String(15),  nullable=False)
    city = Column(String(255), nullable=False)
    neighborhood = Column(String(255), nullable=False)
    blood_type = Column(SQLAEnum(BloodType), nullable=False)
    skill_level = Column(SQLAEnum(SkillLevel), nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)



    # Relación con User especificando el foreign_key
    user = relationship("User", back_populates="person", uselist=False, cascade="all, delete")
