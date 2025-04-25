from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.domain.token import AuthToken


# Crea y guarda un nuevo token en la base de datos

def create_token(db: Session, token: AuthToken):
    try:
        db.add(token)
        db.commit()
        db.refresh(token)
        return True
    except IntegrityError as ie:
        db.rollback()
        return False


def verify_token(db: Session, code: int):
    db_token = db.query(AuthToken).filter(AuthToken.value == code).first()
    if db_token:
        if db_token.date_expiration >= datetime.utcnow() and not db_token.is_used:
            return True, db_token.user_id
        else:
            return False, db_token.user_id
    return None, None


def read_token_by_code(db: Session, code: int):
    return db.query(AuthToken).filter(AuthToken.value == code).first()


def update_token(db: Session, token: AuthToken):
    db_token = db.query(AuthToken).filter(AuthToken.id == token.id).first()
    try:
        db.merge(db_token)
        db.commit()
        return {"detail": "Contraseña actualizada"}
    except IntegrityError as ie:
        db.rollback()
        return HTTPException(status_code=403, detail="No se pudo actualizar.")


def mark_token_as_used(db: Session, code: int):
    db_token = db.query(AuthToken).filter(AuthToken.value == code).first()
    if db_token:
        db_token.is_used = True
        db.add(db_token)
        db.commit()
    return db_token