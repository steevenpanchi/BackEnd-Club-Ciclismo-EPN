from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.endpoints import auth, event, route
from app.core.init_data import create_admin_user
from app.db.init_db import init_db

app = FastAPI(
    description="**Trabajo de Titulación Aplicativo Web para el Club de Ciclismo EPN**",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(event.router, prefix="/event", tags=["event"])
app.include_router(route.router, prefix="/route", tags=["route"])


@app.on_event("startup")
def on_startup():
    init_db()  # Inicializa la base de datos
    create_admin_user()  # Crea el usuario admin si no existe
