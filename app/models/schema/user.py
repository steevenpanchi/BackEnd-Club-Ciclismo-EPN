from pydantic import BaseModel
from enum import Enum
from typing import Optional
from pydantic import EmailStr, Field

from app.models.schema.persona import PersonaCreate, PersonaBase, PersonaResponse


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str  # Usamos el email en lugar del username

# Enum para los roles de usuario
class Role(str, Enum):
    ADMIN = "Admin"
    NORMAL = "Normal"


# Esquema base para los datos de un usuario (todos los campos son requeridos)
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: Role = Role.NORMAL
    persona: PersonaCreate


# Esquema para la respuesta de usuario (incluye la información de la persona asociada)
class UserResponse(UserBase):
    id: int
    role: Role
    person: PersonaResponse

    class Config:
        from_attributes = True


# Esquema para actualizar los datos de un usuario
class UserUpdate(BaseModel):
    role: Optional[Role] = None


    class Config:
        from_attributes = True

class RegisterUser(PersonaCreate):
    email: EmailStr
    password: str

class UserWithPersonaResponse(BaseModel):
    id: int
    role: Role

    person: PersonaResponse  # Se incluye la persona asociada

    class Config:
        from_attributes = True
