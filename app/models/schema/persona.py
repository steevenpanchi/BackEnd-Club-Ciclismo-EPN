from pydantic import BaseModel
from typing import Optional

from app.models.domain.persona import SkillLevel, BloodType


# Esquema base para los datos personales (todos los campos son requeridos)
class PersonaBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    city: str
    neighborhood: str
    blood_type: BloodType
    skill_level: SkillLevel
    profile_picture: Optional[str] = None


# Esquema para crear una nueva persona
class PersonaCreate(PersonaBase):
    pass

class PersonaResponse(PersonaBase):
    id: int

    class Config:
        from_attributes = True


# Esquema para actualizar los datos de una persona
class PersonaUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    blood_type: Optional[BloodType] = None
    skill_level: Optional[SkillLevel] = None
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True