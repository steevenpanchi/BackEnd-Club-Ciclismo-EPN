from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud.route import create_route, get_routes, update_route, delete_route
from app.db.session import get_db
from app.models.domain.user import Role
from app.models.schema.route import RouteCreate, RouteResponse, RouteUpdate
from app.models.schema.user import TokenData

router = APIRouter()


@router.post("/create", response_model=RouteResponse)
def create_route_endpoint(route_data: RouteCreate, db: Session = Depends(get_db),
                          current_user: TokenData = Depends(get_current_user)
                          ):
    """
    Create a New Route / Crear una Nueva Ruta

    English:
    --------
    Register a new cycling route.

    - **name** (required): Name of the route.
    - **start_point** (required): Starting location of the route.
    - **end_point** (required): Ending location of the route.
    - **duration** (required): Estimated duration of the route in minutes.

    Español:
    --------
    Registrar una nueva ruta de ciclismo.

    - **name** (requerido): Nombre de la ruta.
    - **start_point** (requerido): Punto de inicio de la ruta.
    - **end_point** (requerido): Punto final de la ruta.
    - **duration** (requerido): Duración estimada de la ruta en minutos.
    """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_route = create_route(db, route_data)

    if db_route:
        return db_route
    raise HTTPException(status_code=400, detail="Error creating route")


@router.get("/", response_model=List[RouteResponse])
def get_routes_all(db: Session = Depends(get_db),
                   current_user: TokenData = Depends(get_current_user)
                   ):
    """
        Get All Routes / Obtener todas las rutas

        English:
        --------
        Retrieve all registered cycling routes.

        Español:
        --------
        Recuperar todas las rutas de ciclismo registradas.
        """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    routes = get_routes(db)
    return routes

@router.delete("/delete/{route_id}", response_model=RouteResponse)
def delete_route_endpoint(route_id: int, db: Session = Depends(get_db),
                          current_user: TokenData = Depends(get_current_user)):
    """
       Delete Route by ID / Eliminar ruta por ID

       English:
       --------
       Delete a cycling route by its ID.

       - **route_id** (required): ID of the route to delete.

       Español:
       --------
       Eliminar una ruta de ciclismo por su ID.

       - **route_id** (requerido): ID de la ruta a eliminar.
       """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    deleted_route = delete_route(db, route_id)
    if deleted_route:
        return deleted_route
    raise HTTPException(status_code=404, detail="Route not found")
