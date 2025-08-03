#integracion del Pipeline ETL 
from etl_pipeline import run_etl, BiodiversityETLPipeline, insert_sample_data
from scheduler import pipeline_scheduler, run_pipeline_manual, get_scheduler_status
import json
from datetime import datetime

def manual_run():
    print("Ejecutando Pipeline ETL de Biodiversidad...")
    
    try:
        result = run_etl()# Ejecutar el pipeline completo
        
        print("\\n💡Resumen de Ejecución:")
        print(f"ꪜEstado: {result['status']}")
        print(f"⏰Tiempo de ejecución: {result['execution_time_seconds']} segundos")
        print(f"📄Registros extraídos: {result['records_extracted']}")
        print(f"↻Registros transformados: {result['records_transformed']}")
        print(f"🏁Registros cargados: {result['records_loaded']}")
        print(f"⛔Registros rechazados: {result['records_rejected']}")
        print(f"✮Score de calidad: {result['data_quality_score']}%")
        
        if result['backup_files']:
            print("\\n💾Archivos de backup creados:")
            for backup in result['backup_files']:
                print(f"  - {backup['filename']} ({backup['size']})")
        
        if result['errors']:
            print("\\n⚠️Errores encontrados:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print(f"\\n📝Log detallado: {result['log_file']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error ejecutando pipeline: {str(e)}"
        print(f"✖{error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

def setup_sample_data():
    """datos de prueba para el pipeline"""
    print("Configurando datos para prueba...")
    insert_sample_data()
    print(":D Datos de prueba insertados!")

def get_pipeline_metrics():
    """get métricas del pipeline"""
    try:
        #estado del scheduler
        scheduler_status = get_scheduler_status()
        
        #crear las metricas
        metrics = {
            "pipeline_status":"ready",
            "scheduler_running":scheduler_status["scheduler_running"],
            "last_execution":scheduler_status["last_execution"],
            "next_scheduled_run":scheduler_status["next_scheduled_run"],
            "total_executions":scheduler_status["total_executions"],
            "recent_executions":scheduler_status["recent_executions"],
            "timestamp":datetime.now().isoformat()
        }
        
        return metrics
        
    except Exception as e:
        return {
            "pipeline_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def start_automated_pipeline():
    """start pipeline auto"""
    try:
        pipeline_scheduler.start_scheduler()
        return {
            "status": "success",
            "message": "Pipeline automatizado iniciado",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error iniciando pipeline: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def stop_automated_pipeline():
    """stop pipeline auto"""
    try:
        pipeline_scheduler.stop_scheduler()
        return {
            "status": "success",
            "message": "Pipeline automatizado detenido",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deteniendo pipeline: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def configure_pipeline_schedule(config):
    """confi horario del pipeline"""
    try:
        success = pipeline_scheduler.update_config(config)
        if success:
            return {
                "status": "success",
                "message": "Configuración actualizada",
                "config": config,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": "Error actualizando configuración del horario",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configurando pipeline: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

#funciones extras
def get_backup_files():
    """lista de archivos de backup"""
    import os
    import glob
    from pathlib import Path
    
    backup_info= {
        "raw_backups":[],
        "cleaned_backups":[],
        "total_size": 0
    }
    
    try:
        #look for backups RAW
        raw_path= Path("backups/raw")
        if raw_path.exists():
            for file_path in raw_path.glob("*.csv"):
                stat = file_path.stat()
                backup_info["raw_backups"].append({
                    "filename": file_path.name,
                    "size": f"{stat.st_size / 1024:.1f} KB",
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "path": str(file_path)
                })
                backup_info["total_size"] += stat.st_size
        
        #buscar cleans
        cleaned_path= Path("backups/cleaned")
        if cleaned_path.exists():
            for file_path in cleaned_path.glob("*.csv"):
                stat = file_path.stat()
                backup_info["cleaned_backups"].append({
                    "filename": file_path.name,
                    "size":f"{stat.st_size / 1024:.1f} KB",
                    "created":datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "path":str(file_path)
                })
                backup_info["total_size"] += stat.st_size
        
        backup_info["total_size"] = f"{backup_info['total_size'] / 1024:.1f} KB"
        
    except Exception as e:
        backup_info["error"] = str(e)
    
    return backup_info

def get_log_files():
    """get lista de archivos de log"""
    import os
    from pathlib import Path
    
    log_info = {
        "pipeline_logs": [],
        "scheduler_logs": [],
        "json_logs": []
    }
    
    try:
        log_path = Path("logs")
        if log_path.exists(): #logs del pipe
            for file_path in log_path.glob("pipeline_*.log"):
                stat = file_path.stat()
                log_info["pipeline_logs"].append({
                    "filename": file_path.name,
                    "size": f"{stat.st_size / 1024:.1f} KB",
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "path": str(file_path)
                })
            
            #logs del scheduler
            for file_path in log_path.glob("scheduler*.log"):
                stat = file_path.stat()
                log_info["scheduler_logs"].append({
                    "filename": file_path.name,
                    "size": f"{stat.st_size / 1024:.1f} KB",
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "path": str(file_path)
                })
            
            #y del JSON detallado
            for file_path in log_path.glob("pipeline_log_*.json"):
                stat = file_path.stat()
                log_info["json_logs"].append({
                    "filename": file_path.name,
                    "size": f"{stat.st_size / 1024:.1f} KB",
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "path": str(file_path)
                })
    
    except Exception as e:
        log_info["error"] = str(e)
    
    return log_info

#testing
if __name__ == "__main__":
    print("🧪 Probando Pipeline ETL de Biodiversidad")
    print("=" * 50)
    
    #data
    setup_sample_data()
    
    print("\\n" + "=" * 50)
    
    #ejecutar manual
    result = manual_run()
    
    print("\\n" + "=" * 50)
    
    #show metricas
    print("Métricas del Pipeline:")
    metrics = get_pipeline_metrics()
    print(json.dumps(metrics, indent=2, default=str))
    
    print("\\n" + "=" * 50)
    
    #archivos del backup
    print("Archivos de Backup:")
    backups = get_backup_files()
    print(json.dumps(backups, indent=2, default=str))
    
    print("\\nPrueba completada!!!")