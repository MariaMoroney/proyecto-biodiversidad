# models.py - Modelos para especies marinas
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class RawMarineData(Base):
    """Tabla RAW - Datos sin procesar de avistamientos marinos"""
    __tablename__ = "raw_marine_data"

    id = Column(Integer, primary_key=True, index=True)
    species_name = Column(String(255))  # Nombre de la especie
    location = Column(String(255))  # Ubicación del avistamiento
    latitude = Column(Float)  # Coordenadas
    longitude = Column(Float)
    sighting_date = Column(DateTime)  # Fecha del avistamiento
    observer_name = Column(String(255))  # Nombre del observador
    observer_email = Column(String(255))
    description = Column(Text)  # Descripción del avistamiento
    photo_url = Column(String(500))  # URL de la foto (opcional)
    created_at = Column(DateTime, default=datetime.utcnow)


class CleanedMarineData(Base):
    """Tabla CLEANED - Datos procesados y validados"""
    __tablename__ = "cleaned_marine_data"

    id = Column(Integer, primary_key=True, index=True)
    species_name = Column(String(255), nullable=False)
    species_category = Column(String(100))  # Mamífero, Pez, Reptil, etc.
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sighting_date = Column(DateTime, nullable=False)
    observer_name = Column(String(255), nullable=False)
    observer_email = Column(String(255))
    description = Column(Text)
    photo_url = Column(String(500))
    validation_status = Column(String(50), default="pending")  # pending, confirmed, rejected
    data_quality_score = Column(Float)  # 0.0 a 1.0
    processed_at = Column(DateTime, default=datetime.utcnow)


class PipelineLog(Base):
    """Tabla para logs del pipeline ETL"""
    __tablename__ = "pipeline_logs"

    id = Column(Integer, primary_key=True, index=True)
    execution_date = Column(DateTime, default=datetime.utcnow)
    records_extracted = Column(Integer)
    records_transformed = Column(Integer)
    records_loaded = Column(Integer)
    records_rejected = Column(Integer)
    execution_time_seconds = Column(Float)
    status = Column(String(50))  # success, error, warning
    error_message = Column(Text)
    backup_files = Column(Text)  # JSON con rutas de archivos de respaldo