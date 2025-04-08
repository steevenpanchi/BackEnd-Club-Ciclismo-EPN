import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = (
    "mysql+pymysql://"
    + os.getenv("DATABASE_USER")
    + ":"
    + os.getenv("DATABASE_PASSWORD")
    + "@"
    + os.getenv("DATABASE_HOST")
    + "/"
    + os.getenv("DATABASE_NAME")
)

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Crear una clase base para los modelos
Base = declarative_base()

# Crear un sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
