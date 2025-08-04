import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class EcoVisionTester:
    def __init__(self):
        self.project_root = Path.cwd()
        self.api_url = "http://localhost:8001"
        self.test_results = {
            "start_time": datetime.now(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": []
        }
        self.api_process = None
    
    def print_header(self):
        print("=" * 70)
        print("PRUEBAS Y VALIDACIÓN COMPLETA")
        print("=" * 70)
    
    def log_test(self, test_name: str, passed: bool, message: str = "", warning: bool = False):
        """Registrar resultado de una prueba"""
        self.test_results["tests_run"] += 1
        
        if passed:
            self.test_results["tests_passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results["tests_failed"] += 1
            status = "❌ FAIL"
            self.test_results["errors"].append(f"{test_name}: {message}")
        
        if warning:
            self.test_results["warnings"].append(f"{test_name}: {message}")
            status += " ⚠️"
        
        print(f"{status} | {test_name}")
        if message:
            print(f"      {message}")
    
    def test_file_structure(self):
        """Verificar estructura"""
        print("\\nPRUEBA 1: Estructura de archivos")
        print("-" * 40)
        
        required_files = [
            "main.py", "etl_pipeline.py", "scheduler.py", "pipeline.py",
            "database.py", "models.py", "schemas.py", "crud.py"
        ]
        
        required_dirs = [
            "logs", "backups", "backups/raw", "backups/cleaned", "temp"
        ]
        
        #checar
        for file_name in required_files:
            file_path = self.project_root / file_name
            exists = file_path.exists()
            self.log_test(f"Archivo {file_name}", exists, 
                         "" if exists else f"Archivo {file_name} no encontrado")
        
        #verificar los directorios
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists()
            self.log_test(f"Directorio {dir_name}", exists,
                         "" if exists else f"Directorio {dir_name} no encontrado")
    
    def test_python_imports(self):
        """verificar todos los modulos"""
        print("\\nPRUEBA 2: Importación de módulos")
        print("-" * 40)
        
        modules_to_test = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("sqlalchemy", "Database ORM"),
            ("pandas", "Data manipulation"),
            ("schedule", "Task scheduling"),
            ("database", "Database configuration"),
            ("models", "Database models"),
            ("etl_pipeline", "ETL Pipeline"),
            ("pipeline", "Pipeline integration")
        ]
        
        for module_name, description in modules_to_test:
            try:
                __import__(module_name)
                self.log_test(f"Import {module_name}", True, description)
            except ImportError as e:
                self.log_test(f"Import {module_name}", False, f"Error: {str(e)}")
            except Exception as e:
                self.log_test(f"Import {module_name}", False, f"Error inesperado: {str(e)}")
    
    def test_database_connection(self):
        """conexión a la base de datos"""
        print("\\n!!PRUEBA 3: Conexión a base de datos")
        print("-" * 40)
        
        try:
            from database import SessionLocal, engine, create_tables
            
            #probar las conexiones
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            self.log_test("Conexión a BD", True, "Conexión exitosa")
            
            #do tablas
            create_tables()
            self.log_test("Creación de tablas", True, "Tablas creadas/verificadas")
            
        except Exception as e:
            self.log_test("Conexión a BD", False, f"Error: {str(e)}")
    
    def test_etl_pipeline_functionality(self):
        """funcionalidad del pipeline"""
        print("\\n!!!PRUEBA 4: Funcionalidad del Pipeline ETL")
        print("-" * 40)
        
        try:
            from etl_pipeline import insert_sample_data, run_etl
            
            #insertar datos de prueba
            print("   !!! Insertando datos de prueba...")
            insert_sample_data()
            self.log_test("Inserción datos prueba", True, "Datos de prueba insertados")
            
            #pipeline
            print("   Ejecutando pipeline ETL...")
            result = run_etl()
            
            #resultados
            if result.get("status") == "success":
                self.log_test("Ejecución ETL", True, 
                             f"Procesados: {result.get('records_loaded', 0)} registros")
            else:
                self.log_test("Ejecución ETL", False, 
                             f"Status: {result.get('status', 'unknown')}")
            
            #métricas
            metrics = ["records_extracted", "records_transformed", "records_loaded"]
            for metric in metrics:
                value = result.get(metric, 0)
                self.log_test(f"Métrica {metric}", value > 0, f"Valor: {value}")
            
        except Exception as e:
            self.log_test("Pipeline ETL", False, f"Error: {str(e)}")
    
    def start_api_server(self):
        """iniciar servidor API """
        print("\\n!!!PRUEBA 5: Servidor API")
        print("-" * 40)
        
        try:
            #iniciar servidor
            self.api_process = subprocess.Popen([
                sys.executable, "main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("   Esperando inicio del servidor...")
            time.sleep(5)
            
            #verifica que este corriendo
            if self.api_process.poll() is None:
                self.log_test("Inicio servidor API", True, "Servidor iniciado en puerto 8001")
                return True
            else:
                self.log_test("Inicio servidor API", False, "Servidor no pudo iniciar")
                return False
                
        except Exception as e:
            self.log_test("Inicio servidor API", False, f"Error: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """probar endpoints de la API"""
        print("\\n!!!PRUEBA 6: Endpoints de la API")
        print("-" * 40)
        
        endpoints_to_test = [
            ("GET", "/health", "Health check"),
            ("GET", "/api/dashboard/stats", "Dashboard stats"),
            ("GET", "/api/species", "Species list"),
            ("GET", "/api/scheduler/status", "Scheduler status"),
            ("POST", "/api/pipeline/run", "Pipeline execution"),
            ("GET", "/api/pipeline/metrics", "Pipeline metrics")
        ]
        
        for method, endpoint, description in endpoints_to_test:
            try:
                url = f"{self.api_url}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, timeout=10)
                elif method == "POST":
                    response = requests.post(url, json={}, timeout=30)
                
                if response.status_code == 200:
                    self.log_test(f"{method} {endpoint}", True, description)
                else:
                    self.log_test(f"{method} {endpoint}", False, 
                                 f"Status: {response.status_code}")
                
            except requests.exceptions.ConnectionError:
                self.log_test(f"{method} {endpoint}", False, "No se pudo conectar al servidor")
            except requests.exceptions.Timeout:
                self.log_test(f"{method} {endpoint}", False, "Timeout en la petición")
            except Exception as e:
                self.log_test(f"{method} {endpoint}", False, f"Error: {str(e)}")
    
    def test_file_generation(self):
        """acá se verifican los archivos"""
        print("\\n!!! PRUEBA 7: Generación de archivos")
        print("-" * 40)
        
        # Verificar logs
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log")) + list(logs_dir.glob("*.json"))
            self.log_test("Archivos de log", len(log_files) > 0, 
                         f"Encontrados {len(log_files)} archivos de log")
        else:
            self.log_test("Archivos de log", False, "Directorio logs no existe")
        
        #verificar los backups
        backups_dir = self.project_root / "backups"
        if backups_dir.exists():
            backup_files = list(backups_dir.rglob("*.csv"))
            self.log_test("Archivos de backup", len(backup_files) > 0,
                         f"Encontrados {len(backup_files)} archivos de backup")
        else:
            self.log_test("Archivos de backup", False, "Directorio backups no existe")
    
    def test_scheduler_functionality(self):
        """funcionalidad del scheduler"""
        print("\\n!!!PRUEBA 8: Funcionalidad del Scheduler")
        print("-" * 40)
        
        try:
            #probar los endpoints del api
            endpoints = [
                ("GET", "/api/scheduler/status", "Estado del scheduler"),
                ("POST", "/api/scheduler/start", "Iniciar scheduler"),
                ("POST", "/api/scheduler/stop", "Detener scheduler")
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.api_url}{endpoint}"
                    
                    if method == "GET":
                        response = requests.get(url, timeout=5)
                    else:
                        response = requests.post(url, json={}, timeout=5)
                    
                    success = response.status_code == 200
                    self.log_test(f"Scheduler {description}", success,
                                 f"Status: {response.status_code}" if not success else "")
                    
                except Exception as e:
                    self.log_test(f"Scheduler {description}", False, f"Error: {str(e)}")
                    
        except Exception as e:
            self.log_test("Scheduler functionality", False, f"Error general: {str(e)}")
    
    def cleanup(self):
        """limpiar todo despues de las pruebas"""
        print("\\n🧹 limpiandoo...")
        
        # Terminar servidor API
        if self.api_process and self.api_process.poll() is None:
            self.api_process.terminate()
            time.sleep(2)
            if self.api_process.poll() is None:
                self.api_process.kill()
            print(" Servidor API terminado")
    
    def generate_report(self):
        """reporte final"""
        end_time = datetime.now()
        duration = end_time - self.test_results["start_time"]
        
        print("\\n" + "=" * 70)
        print("reporte final de las pruebas")
        print("=" * 70)
        
        print(f"⏰ Duración total: {duration.total_seconds():.1f} segundos")
        print(f"🧪 Pruebas ejecutadas: {self.test_results['tests_run']}")
        print(f"✔️ Pruebas exitosas: {self.test_results['tests_passed']}")
        print(f"❌ Pruebas fallidas: {self.test_results['tests_failed']}")
        print(f"⚠️  Advertencias: {len(self.test_results['warnings'])}")
        
        # % de exito
        if self.test_results['tests_run'] > 0:
            success_rate = (self.test_results['tests_passed'] / self.test_results['tests_run']) * 100
            print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        #mostrar los errores en caso de que los haya
        if self.test_results['errors']:
            print("\\n ERRORES:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        # y advertencias
        if self.test_results['warnings']:
            print("\\n ADVERTENCIAS:")
            for warning in self.test_results['warnings']:
                print(f"   • {warning}")
        
        #recomendaciones
        print("\\n🎯 RECOMENDACIONES:")
        if self.test_results['tests_failed'] == 0:
            print("  Todas las pruebas pasaron! El sistema está listo para producción.")
        elif self.test_results['tests_failed'] < 3:
            print(" Hay algunos problemas menores: Revisa antes de desplegar.")
        else:
            print(" Hay problemas significativos: se requiere la revision inmmediata.")
        
        print("\\nin case: revisar README.md")
        print("=" * 70)
        
        #guardar reporte
        report_file = self.project_root / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump({
                    **self.test_results,
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration.total_seconds(),
                    "success_rate": (self.test_results['tests_passed'] / max(self.test_results['tests_run'], 1)) * 100
                }, f, indent=2, default=str)
            print(f"\\nReporte guardado en: {report_file}")
        except Exception as e:
            print(f"\\nNo se pudo guardar el reporte: {e}")
    



    def run_all_tests(self):
        self.print_header()
        
        try:
            #pruebas sin servidor
            self.test_file_structure()
            self.test_python_imports()
            self.test_database_connection()
            self.test_etl_pipeline_functionality()
            
            #iniciar servidor para las pruebas del api
            if self.start_api_server():
                time.sleep(2) #ocupa tiempito
                self.test_api_endpoints()
                self.test_scheduler_functionality()
            
            #pruebas de los archivos generados
            self.test_file_generation()
            
        except KeyboardInterrupt:
            print("\\n\\nPruebas interrumpidas por el usuario")
        except Exception as e:
            print(f"\\n\\nError crítico durante las pruebas: {e}")
        finally:
            self.cleanup()
            self.generate_report()

if __name__ == "__main__":
    print("🧪 Iniciando pruebas del sistema...")
    print("   (Presiona Ctrl+C para interrumpir en cualquier momento)")
    print()
    
    tester = EcoVisionTester()
    tester.run_all_tests()