from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.domain.user import User, Role
from app.models.schema.user import UserCreate, UserUpdate
from app.models.domain.persona import Persona
from app.crud.persona import create_persona
from app.services.crypt import get_password_hash, verify_password
from app.services.verify import verify_email, verify_structure_password

def create_user(db: Session, user_data: UserCreate):
    # Validar el correo electrónico
    if not verify_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Correo electrónico no válido."
        )
        # Verificar si el correo ya está en uso
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado."
        )

    # Validar la contraseña
    if not verify_structure_password(user_data.password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula y un número."
        )

    # Verificar si `persona` está presente antes de acceder a sus atributos
    if not hasattr(user_data, "persona") or user_data.persona is None:
        raise HTTPException(
            status_code=400,
            detail="El campo 'persona' es obligatorio."
        )
    # Verificar si el número de teléfono ya está registrado
    existing_persona = db.query(Persona).filter(Persona.phone_number == user_data.persona.phone_number).first()
    if existing_persona:
        raise HTTPException(status_code=400, detail="El número de teléfono ya está registrado.")

    # Crear la persona primero
    new_person = Persona(**user_data.persona.model_dump())  # Usa `.model_dump()` si usas Pydantic v2
    db.add(new_person)
    db.commit()
    db.refresh(new_person)

    # Crear el usuario con la persona asociada y sin imagen de perfil
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,  # No necesitas una validación, ya que 'role' tiene un valor predeterminado
        person_id=new_person.id,  # Enlazamos con la persona creada
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Validar el correo electrónico si se está actualizando
    if user_data.email and not verify_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Correo electrónico no válido."
        )

    # Validar la contraseña si se está actualizando
    if user_data.password and not verify_structure_password(user_data.password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula y un número."
        )

    # Si se ha pasado algún campo de correo o contraseña, lo actualizamos
    if user_data.email:
        db_user.email = user_data.email

    if user_data.password:
        db_user.hashed_password = get_password_hash(user_data.password)  # Asegúrate de cifrar la contraseña

    if user_data.role:
        db_user.role = user_data.role

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    db.delete(user)
    db.commit()
    return {"detail": "Usuario eliminado correctamente"}


def get_all_users(db: Session):
    return db.query(User).all()


def get_user_id_by_email(db: Session, user_email: str):
    """
    Devuelve el ID de un usuario basado en su correo electrónico.
    Si no se encuentra el usuario, devuelve un error como texto plano.
    """

    # Validar la estructura del email
    if not verify_email(user_email):
        # Devuelve texto plano, no un "detail"
        raise HTTPException(status_code=400, detail="Correo electrónico no válido.")

    # Buscar el usuario
    user = db.query(User).filter(User.email == user_email).first()

    if user:
        return user.id
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado con este correo electrónico.")

def update_password(db: Session, user_id: int, new_password: str):
    user = get_user_by_id(db, user_id)

    if user:
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        return user


