import base64

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.domain.persona import Persona
from app.models.domain.user import User
from app.models.schema.persona import PersonaCreate, PersonaUpdate, PersonaBase
from app.services.verify import verify_cellphone_number, verify_location_field, verify_image_size


def create_persona(db: Session, persona_data: PersonaCreate):
    # Validar número de teléfono
    if not verify_cellphone_number(persona_data.phone_number):
        raise HTTPException(status_code=400,
                            detail="Número de teléfono inválido. Debe tener entre 7 y 10 dígitos numéricos.")

    # Validar ciudad y barrio
    persona_data.city = verify_location_field(persona_data.city, "Ciudad")
    persona_data.neighborhood = verify_location_field(persona_data.neighborhood, "Barrio")

    # Verificar si el número de teléfono ya está registrado
    existing_persona = db.query(Persona).filter(Persona.phone_number == persona_data.phone_number).first()
    if existing_persona:
        raise HTTPException(status_code=400, detail="El número de teléfono ya está registrado.")

    try:
        new_persona = Persona(**persona_data.dict())
        db.add(new_persona)
        db.commit()
        db.refresh(new_persona)
        return new_persona
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El número de teléfono ya está registrado.")


def get_persona_by_id(db: Session, persona_id: int):
    return db.query(Persona).filter(Persona.id == persona_id).first()


def get_all_personas(db: Session):
    return db.query(Persona).all()

def update_persona(db: Session, persona_id: int, persona_data: PersonaUpdate):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada.")

    update_data = persona_data.dict(exclude_unset=True)

    # Validación del número de teléfono
    if "phone_number" in update_data and not verify_cellphone_number(update_data["phone_number"]):
        raise HTTPException(
            status_code=400,
            detail="Número de teléfono inválido. Debe tener entre 7 y 10 dígitos numéricos."
        )

    # Validación de ubicación
    if "city" in update_data:
        update_data["city"] = verify_location_field(update_data["city"], "Ciudad")
    if "neighborhood" in update_data:
        update_data["neighborhood"] = verify_location_field(update_data["neighborhood"], "Barrio")

    # Si se envía imagen base64, convertirla a bytes y validar
    if "profile_picture" in update_data:
        update_data["profile_picture"] = verify_image_size(update_data["profile_picture"])
        persona.profile_picture = update_data["profile_picture"]

    # Aplicar cambios
    for key, value in update_data.items():
        setattr(persona, key, value)

    db.commit()
    db.refresh(persona)
    return persona
def delete_persona(db: Session, persona_id: int):
    persona = get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    try:
        db.delete(persona)
        db.commit()
        return {"detail": "Persona eliminada correctamente"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar la persona")
