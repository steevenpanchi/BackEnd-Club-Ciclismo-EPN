from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.staticfiles import StaticFiles

from app.api.endpoints import auth, event, route, event_participant
from app.core.init_data import create_admin_user
from app.db.init_db import init_db

app = FastAPI(

)

# 🟢 Permitir peticiones CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Incluir rutas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(event.router, prefix="/event", tags=["event"])
app.include_router(route.router, prefix="/route", tags=["route"])
app.include_router(event_participant.router, prefix="/participants", tags=["participants"])


# ⚙️ Inicializar base de datos y crear admin
@app.on_event("startup")
def on_startup():
    init_db()
    create_admin_user()

# 🔐 Personalización de la documentación con token de email/contraseña
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Club de Ciclismo EPN",
        version="1.0.0",
        description="**Trabajo de Titulación Aplicativo Web para el Club de Ciclismo EPN**",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/token",
                    "scopes": {},
                }
            },
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
