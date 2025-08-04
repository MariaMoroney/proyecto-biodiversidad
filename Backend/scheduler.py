
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os
from pathlib import Path

# Importar el pipeline ETL
from etl_pipeline import run_etl, BiodiversityETLPipeline

class PipelineScheduler:
    """automatizacion del inicio del pipeline"""
    
    def __init__(self):
        self.setup_logging()
        self.is_running = False
        self.scheduler_thread = None
        self.last_execution = None
        self.execution_history = []
        self.config_file = "scheduler_config.json"
        self.load_config()
    
    def setup_logging(self):
        """logging para el scheduler"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "scheduler.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("PipelineScheduler")
    
    def load_config(self):
        default_config = {
            "enabled": True,
            "schedule_type": "daily",  #daily, hourly, weekly, custom
            "schedule_time": "02:00",  #daily/weekly
            "schedule_interval": 1,    #hourly (cada X horas)
            "schedule_day": "monday",  #weekly
            "custom_cron": None,       #custom
            "max_execution_history": 100,
            "email_notifications": False,
            "email_recipients": [],
            "retry_attempts": 3,
            "retry_delay_minutes": 5
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = {**default_config, **json.load(f)}
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error de configuración: {e}")
            self.config = default_config
    
    def save_config(self):
        """guardar configuración"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
    

    def setup_schedule(self):
        """configurar horarios"""
        schedule.clear() 
        
        if not self.config["enabled"]:
            self.logger.info("Scheduler deshabilitado en configuración")
            return
        
        schedule_type = self.config["schedule_type"]
        
        if schedule_type == "daily":
            schedule.every().day.at(self.config["schedule_time"]).do(self.run_scheduled_pipeline)
            self.logger.info(f"Pipeline programado diariamente a las {self.config['schedule_time']}")
        
        elif schedule_type == "hourly":
            interval = self.config["schedule_interval"]
            schedule.every(interval).hours.do(self.run_scheduled_pipeline)
            self.logger.info(f"Pipeline programado cada {interval} hora(s)")
        
        elif schedule_type == "weekly":
            day = self.config["schedule_day"]
            time_str = self.config["schedule_time"]
            getattr(schedule.every(), day).at(time_str).do(self.run_scheduled_pipeline)
            self.logger.info(f"Pipeline programado semanalmente los {day} a las {time_str}")
        
        elif schedule_type == "custom":
            #in case
            self.logger.warning("⚠️ Horario personalizado no implementado aún")
        
        else:
            self.logger.error(f"D: Tipo de horario no válido: {schedule_type}")
    
    def run_scheduled_pipeline(self):
        """ejecutar pipeline"""
        execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger.info(f"Iniciando ejecución programada {execution_id}")
        
        execution_record = {
            "execution_id": execution_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "running",
            "attempts": 0,
            "result": None,
            "error": None
        }
        
#ejecutar
        max_attempts = self.config["retry_attempts"]
        retry_delay = self.config["retry_delay_minutes"]
        
        for attempt in range(1, max_attempts + 1):
            try:
                execution_record["attempts"] = attempt
                self.logger.info(f"↻ Intento {attempt}/{max_attempts}")
                
                #ejecutar
                result = run_etl()
                
                #verificar si cargó
                if result["status"] == "success":
                    execution_record["status"] = "success"
                    execution_record["result"] = result
                    execution_record["end_time"] = datetime.now().isoformat()
                    
                    self.logger.info(f"Pipeline ejecutado exitosamente en intento {attempt}")
                    self.last_execution = execution_record
                    break
                
                else:
                    raise Exception(f"Pipeline falló: {result.get('errors', [])}")
            
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Error en intento {attempt}: {error_msg}")
                
                execution_record["error"] = error_msg
                
                if attempt < max_attempts:
                    self.logger.info(f"↻ ◌⏳Esperando {retry_delay} minutos antes del siguiente intento...")
                    time.sleep(retry_delay * 60)
                else:
                    execution_record["status"] = "failed"
                    execution_record["end_time"] = datetime.now().isoformat()
                    self.last_execution = execution_record
                    
                    #enviar error 
                    if self.config["email_notifications"]:
                        self.send_error_notification(execution_record)
        


        #guardar en el historial
        self.execution_history.append(execution_record)
        
        #mantener solo las últimas N ejecuciones
        max_history = self.config["max_execution_history"]
        if len(self.execution_history) > max_history:
            self.execution_history = self.execution_history[-max_history:]
        
        #guardar
        self.save_execution_history()
    
    def send_error_notification(self, execution_record: Dict):
        """sent notificación de error por email (placeholder)"""
        self.logger.info("Enviando notificación de error...")
        
        #log
        self.logger.error(f"ALERTA: Pipeline falló después de {execution_record['attempts']} intentos")
        self.logger.error(f"Error: {execution_record['error']}")
    


    def save_execution_history(self):
        try:
            history_file = "logs/execution_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_history, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error guardando historial: {e}")
    
    
    def start_scheduler(self):
        if self.is_running:
            self.logger.warning("Scheduler ya está ejecutándose")
            return
        
        self.setup_schedule()
        self.is_running = True
        
        def run_scheduler():
            self.logger.info("Scheduler iniciado")
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  #checar x minuto
                except Exception as e:
                    self.logger.error(f"Error en scheduler: {e}")
                    time.sleep(60)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Scheduler iniciado!!")
    
    def stop_scheduler(self):
        """stop el scheduler"""
        if not self.is_running:
            self.logger.warning("Scheduler no está ejecutándose")
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("⛔Scheduler detenido")
    
    def run_manual(self) -> Dict:
        """ejecutar manual"""
        self.logger.info("🔧 Ejecución manual del pipeline")
        
        try:
            result = run_etl()
            
            #registrar
            execution_record = {
                "execution_id": f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "status": result["status"],
                "attempts": 1,
                "result": result,
                "error": None,
                "type": "manual"
            }
            
            self.execution_history.append(execution_record)
            self.save_execution_history()
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error en ejecución: {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict:
        """obtener estado"""
        next_run = None
        if self.is_running and schedule.jobs:
            next_run = schedule.next_run()
        
        return {
            "scheduler_running": self.is_running,
            "config": self.config,
            "next_scheduled_run": next_run.isoformat() if next_run else None,
            "last_execution": self.last_execution,
            "total_executions": len(self.execution_history),
            "recent_executions": self.execution_history[-5:] if self.execution_history else []
        }
    
    def update_config(self, new_config: Dict):
        """actualizar scheduler"""
        try:
            self.config.update(new_config)
            self.save_config()
            
            #reiniciar en caso de que ya estuviera funcionando antes
            if self.is_running:
                self.stop_scheduler()
                self.start_scheduler()
            
            self.logger.info("ꪜ Configuración actualizada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando: {e}")
            return False

