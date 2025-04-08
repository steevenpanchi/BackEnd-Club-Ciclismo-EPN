from sqlalchemy.orm import Session
from app.db.database import SessionLocal


# se obtiene la sesión para hacer las operaciones crud
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()