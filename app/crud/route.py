from fastapi import HTTPException

from sqlalchemy.orm import Session
from app.models.domain.route import Route
from app.models.schema.route import RouteCreate, RouteUpdate

def create_route(db: Session, route_data: RouteCreate):
    new_route = Route(**route_data.dict())
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    return new_route

def get_routes(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Route).offset(skip).limit(limit).all()

def update_route(db: Session, route_id: int, route_data: RouteUpdate):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        return None
    for key, value in route_data.dict(exclude_unset=True).items():
        setattr(route, key, value)
    db.commit()
    db.refresh(route)
    return route

def delete_route(db: Session, route_id: int):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    if route.events:  # ⚠️ Verifica si tiene eventos asociados
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la ruta porque está asociada a uno o más eventos."
        )

    db.delete(route)
    db.commit()
    return route