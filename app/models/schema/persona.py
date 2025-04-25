import base64
from typing import Optional

from pydantic import BaseModel

from app.models.domain.persona import SkillLevel, BloodType


# Esquema base para datos personales
class PersonaBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    city: str
    neighborhood: str
    blood_type: BloodType
    skill_level: SkillLevel
    profile_picture: Optional[str] = None


# Crear persona (registro)
class PersonaCreate(PersonaBase):
    pass


# Actualizar datos parcialmente
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


class PersonaResponse(PersonaBase):
    id: int

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Convertir imagen de bytes a base64 con encabezado
        profile_picture = None
        if obj.profile_picture and isinstance(obj.profile_picture, (bytes, bytearray)):
            try:
                profile_picture = f"data:image/png;base64,{base64.b64encode(obj.profile_picture).decode()}"
            except Exception:
                profile_picture = None

        return cls(
            id=obj.id,
            first_name=obj.first_name,
            last_name=obj.last_name,
            phone_number=obj.phone_number,
            city=obj.city,
            neighborhood=obj.neighborhood,
            blood_type=obj.blood_type,
            skill_level=obj.skill_level,
            profile_picture=profile_picture
        )
