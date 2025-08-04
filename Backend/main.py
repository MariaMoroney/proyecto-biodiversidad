# main.py - Backend mínimo funcional para EcoVision
from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import uvicorn
from scheduler import PipelineScheduler
from typing import Dict
from pipeline import (
    manual_run,
    get_pipeline_metrics,
    get_backup_files,
    get_log_files,
    start_automated_pipeline,
    stop_automated_pipeline,
    configure_pipeline_schedule
)

from database import get_db, create_tables

create_tables()
app = FastAPI(
    title="EcoVision Marine API",
    description="API para el sistema de monitoreo de especies marinas",
    version="1.0.0"
    )
pipeline_scheduler= PipelineScheduler() #schechule


# Configurar CORS para tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datos mock para pruebas rápidas
MOCK_DASHBOARD_STATS = {
    "totalSightings": 1247,
    "recentSightings": 23,
    "speciesCount": 89,
    "pendingValidation": 12,
    "systemStatus": "En línea"
}

MOCK_SPECIES_DATA = [
    {
        "id": 1,
        "species_name": "Ballena Jorobada",
        "species_category": "Mamífero",
        "location": "Golfo de Papagayo",
        "latitude": 10.5,
        "longitude": -85.8,
        "sighting_date": "2024-01-15T10:30:00Z",
        "observer_name": "Carlos Marín",
        "validation_status": "confirmed",
        "data_quality_score": 0.95
    },
    {
        "id": 2,
        "species_name": "Delfín Nariz de Botella",
        "species_category": "Mamífero",
        "location": "Bahía Drake",
        "latitude": 8.7,
        "longitude": -83.6,
        "sighting_date": "2024-01-20T14:15:00Z",
        "observer_name": "Ana Rodríguez",
        "validation_status": "confirmed",
        "data_quality_score": 0.88
    },
    {
        "id": 3,
        "species_name": "Tortuga Verde",
        "species_category": "Reptil",
        "location": "Playa Ostional",
        "latitude": 10.3,
        "longitude": -85.9,
        "sighting_date": "2024-01-18T08:45:00Z",
        "observer_name": "Miguel Torres",
        "validation_status": "pending",
        "data_quality_score": 0.92
    }
]

MOCK_MAP_DATA = [
    {
        "id": 1,
        "lat": 10.5,
        "lng": -85.8,
        "species": "Ballena Jorobada",
        "location": "Golfo de Papagayo",
        "date": "2024-01-15T10:30:00Z",
        "observer": "Carlos Marín",
        "status": "confirmed"
    },
    {
        "id": 2,
        "lat": 8.7,
        "lng": -83.6,
        "species": "Delfín Nariz de Botella",
        "location": "Bahía Drake",
        "date": "2024-01-20T14:15:00Z",
        "observer": "Ana Rodríguez",
        "status": "confirmed"
    }
]


# ===================== ENDPOINTS PRINCIPALES =====================
# ==== ENDPOINTS DEL SCHEDULER ====

@app.post("/api/scheduler/start")
def start_scheduler():
    """start scheduler auto"""
    result = pipeline_scheduler.start_scheduler()
    return {"status": "success", "message": "Scheduler iniciado", "data": result}

@app.post("/api/scheduler/stop")
def stop_scheduler():
    """stop scheduler auto"""
    result = pipeline_scheduler.stop_scheduler()
    return {"status": "success", "message": "Scheduler detenido", "data": result}

@app.get("/api/scheduler/status")
def get_scheduler_status():
    """obtener estado"""
    return pipeline_scheduler.get_status()

@app.post("/api/scheduler/config")
def update_scheduler_config(config: Dict):
    """update configuración del scheduler"""
    result = pipeline_scheduler.update_config(config)
    return {"status": "success", "message": "Configuración actualizada", "data": result}

@app.post("/api/pipeline/run-manual")
def run_pipeline_manual_scheduler():
    """ejecutar pipeline manualmente through scheduler"""
    return pipeline_scheduler.run_manual()


@app.get("/health")
def health_check():
    """Verificar estado de la API"""
    return {
        "status": "healthy",
        "service": "EcoVision Marine API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """Estadísticas para el dashboard principal"""
    return MOCK_DASHBOARD_STATS


@app.get("/api/sightings/map-data")
def get_map_data():
    """Datos para el mapa de avistamientos"""
    return MOCK_MAP_DATA


@app.get("/api/species")
def get_all_species(skip: int = 0, limit: int = 100):
    """Obtener todas las especies"""
    return MOCK_SPECIES_DATA[skip:skip + limit]


@app.get("/api/species/categories")
def get_species_categories():
    """Obtener categorías de especies para filtros"""
    categories = list(set([species["species_category"] for species in MOCK_SPECIES_DATA]))
    return {
        "categories": categories,
        "total": len(categories)
    }


@app.post("/api/sightings")
def create_sighting(sighting_data: dict):
    """Crear nuevo reporte de avistamiento"""
    # Simular creación de avistamiento
    new_sighting = {
        "id": len(MOCK_SPECIES_DATA) + 1,
        "created_at": datetime.now().isoformat(),
        **sighting_data
    }

    # En producción, aquí guardarías en la base de datos
    print(f"✅ Nuevo avistamiento recibido: {new_sighting}")

    return {
        "status": "success",
        "message": "Avistamiento registrado correctamente",
        "data": new_sighting
    }


@app.post("/api/pipeline/run")
def run_pipeline_manual():
    """Ejecutar pipeline ETL manualmente"""
    # Simular ejecución de pipeline
    import time
    import random

    start_time = time.time()

    # Simular procesamiento
    time.sleep(1)

    execution_time = time.time() - start_time
    records_processed = random.randint(50, 200)

    result = {
        "status": "success",
        "message": "Pipeline ejecutado correctamente",
        "timestamp": datetime.now().isoformat(),
        "records_processed": records_processed,
        "execution_time_seconds": round(execution_time, 2),
        "records_extracted": records_processed,
        "records_transformed": records_processed - 5,
        "records_loaded": records_processed - 8,
        "records_rejected": 8
    }

    print(f"🔄 Pipeline ejecutado: {result}")
    return result


@app.get("/api/pipeline/status")
def get_pipeline_status():
    """Obtener estado actual del pipeline"""
    return {
        "status": "ready",
        "message": "Pipeline listo para ejecutar",
        "last_execution": datetime.now().isoformat(),
        "records_processed": 156,
        "execution_time": 2.34
    }


@app.get("/api/pipeline/logs")
def get_pipeline_logs(limit: int = 10):
    """Obtener logs del pipeline"""
    mock_logs = [
        {
            "id": 1,
            "execution_date": datetime.now().isoformat(),
            "records_extracted": 156,
            "records_transformed": 151,
            "records_loaded": 148,
            "records_rejected": 8,
            "execution_time_seconds": 2.34,
            "status": "success",
            "error_message": None
        }
    ]
    return mock_logs[:limit]


@app.get("/api/cleaned-data")
def get_cleaned_data():
    """Endpoint requerido por el entregable - datos limpios"""
    return MOCK_SPECIES_DATA


# ===================== EVENTOS DE INICIO =====================

@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print("🌊 Iniciando EcoVision Marine API...")
    create_tables()
    
    # Inicializar scheduler
    print("⏰ Inicializando scheduler...")
    pipeline_scheduler.initialize()
    
    print("✅ API lista en http://localhost:8001")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )