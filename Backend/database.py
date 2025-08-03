# database.py - Configuración simple con SQLite
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite para pruebas rápidas (cambia después a PostgreSQL)
DATABASE_URL = "sqlite:///./ecovision_marine.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función para crear las tablas
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas!")

# Función para obtener sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()