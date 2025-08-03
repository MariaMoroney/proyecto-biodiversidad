#script de configuracion, (fue una recomendacion)
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class EcoVisionSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.required_dirs = [
            "logs",
            "backups/raw", 
            "backups/cleaned",
            "temp",
            "config"
        ]
        self.required_files = [
            "database.py",
            "models.py", 
            "etl_pipeline.py",
            "scheduler.py",
            "pipeline.py",
            "main.py"
        ]
    
    def print_header(self):
        print("=" * 60)
        print("ECOVISION PIPELINE ETL - CONFIGURACIÓN AUTOMÁTICA")
        print("=" * 60)
        print(f"Directorio: {self.project_root}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def check_python_version(self):
        print("Verificando versión de Python...")
        if sys.version_info < (3, 8):
            print("ERROR: Se requiere Python 3.8 o superior")
            print(f"   Versión actual: {sys.version}")
            return False
        print(f"Python {sys.version.split()[0]} - OK")
        return True
    
    def create_directories(self):
        print("\\nCreando directorios necesarios...")
        for directory in self.required_dirs:
            dir_path = self.project_root / directory
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"{directory}")
            except Exception as e:
                print(f"Error creando {directory}: {e}")
                return False
        return True
    
    def check_required_files(self):
        print("\\nVerificando archivos requeridos...")
        missing_files = []
        for file_name in self.required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"✅ {file_name}")
            else:
                print(f"❌ {file_name} - fatla!!!")
                missing_files.append(file_name)
        
        if missing_files:
            print(f"\\n ADVERTENCIA: Faltan {len(missing_files)} archivos:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        return True
    
    def install_dependencies(self):
        print("\\nInstalando dependencias...")
        
        #dependencias requeridas
        dependencies = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "sqlalchemy>=2.0.0",
            "pandas>=2.0.0",
            "schedule>=1.2.0",
            "python-multipart>=0.0.6"
        ]
        
        try:
            #en caso de que no exista requirements.txt
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                with open(requirements_file, 'w') as f:
                    f.write("\\n".join(dependencies))
                print("requirements.txt creado")
            
            #instalar las dependencias
            print("Instalando paquetes...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Dependencias instaladas!!")
                return True
            else:
                print(f"Error instalando: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error en: {e}")
            return False
    
    def create_config_files(self):
        print("\\ncreando archivos de configuración...")
        
        #confi del sched
        scheduler_config = {
            "enabled": True,
            "schedule_time": "02:00",
            "schedule_days": ["monday", "wednesday", "friday"],
            "max_retries": 3,
            "retry_delay_minutes": 5,
            "backup_retention_days": 30,
            "log_level": "INFO"
        }
        
        config_file = self.project_root / "config" / "scheduler_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(scheduler_config, f, indent=2)
            print("scheduler_config.json creado")
        except Exception as e:
            print(f"Error creando configuración: {e}")
            return False
        
        #EJEMPLO de confi
        db_config = {
            "database_url": "sqlite:///./biodiversity.db",
            "echo": False,
            "pool_size": 5,
            "max_overflow": 10
        }
        
        db_config_file = self.project_root / "config" / "database_config.json"
        try:
            with open(db_config_file, 'w') as f:
                json.dump(db_config, f, indent=2)
            print("database_config.json creado")
        except Exception as e:
            print(f"Error creando configuración de BD: {e}")
            return False
        
        return True
    
    def create_startup_scripts(self):
        print("\\nCreando scripts de inicio :D...")
        
        # Script para Linux/Mac!!!
        startup_sh = '''#!/bin/bash
echo "Iniciando EcoVision Pipeline ETL..."

#activate entorno
if [ -d "venv" ]; then
    echo " Activando entorno..."
    source venv/bin/activate
fi

#dependencias
echo "Verificando dependencias..."
python -c "import fastapi, uvicorn, sqlalchemy, pandas, schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Faltan dependencias. Ejecuta: pip install -r requirements.txt"
    exit 1
fi

echo "Iniciando servidor..."
python main.py
'''
        
        startup_file = self.project_root / "start.sh"
        try:
            with open(startup_file, 'w') as f:
                f.write(startup_sh)
            # Hacer ejecutable en sistemas Unix
            if os.name != 'nt':
                os.chmod(startup_file, 0o755)
            print("✅ start.sh creado")
        except Exception as e:
            print(f"❌ Error creando start.sh: {e}")
        
        # Script para Windows
        startup_bat = '''@echo off
echo 🌊 Iniciando EcoVision Pipeline ETL...

REM Activar entorno virtual si existe
if exist "venv\\Scripts\\activate.bat" (
    echo 📦 Activando entorno virtual...
    call venv\\Scripts\\activate.bat
)

REM Verificar dependencias
echo 🔍 Verificando dependencias...
python -c "import fastapi, uvicorn, sqlalchemy, pandas, schedule" >nul 2>&1
if errorlevel 1 (
    echo ❌ Faltan dependencias. Ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Iniciar la API
echo 🚀 Iniciando servidor...
python main.py
pause
'''
        
        startup_bat_file = self.project_root / "start.bat"
        try:
            with open(startup_bat_file, 'w') as f:
                f.write(startup_bat)
            print("!! start.bat creado !!")
        except Exception as e:
            print(f"¡¡ Error creando start.bat: {e} ¡¡")
        
        return True
    
    def run_setup(self):
        self.print_header()
        
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Crear directorios", self.create_directories),
            ("Verificar archivos", self.check_required_files),
            ("Instalar dependencias", self.install_dependencies),
            ("Crear configuraciones", self.create_config_files),
            ("Crear scripts de inicio", self.create_startup_scripts)
        ]
        
        success_count = 0
        for step_name, step_function in steps:
            try:
                if step_function():
                    success_count += 1
                else:
                    print(f"\\nPaso '{step_name}' completado con advertencias")
            except Exception as e:
                print(f"\\nError en '{step_name}': {e}")
        
        print("\\n" + "=" * 60)
        print(f" RESUMEN: {success_count}/{len(steps)} pasos completados")
        
        if success_count == len(steps):
            print("Configuración completada!")
            print("\\nPara iniciar el proyecto:")
            print("   Windows:   start.bat")
            print("   Manual:    python main.py")
        else:
            print("Configuración completada con advertencias")
            print("Revisa los mensajes anteriores para más detalles, en caso de tener mac o linux des-comentar la iniciacion en el código")
        
        print("\\nDoc disponible en README.md")
        print("=" * 60)

if __name__ == "__main__":
    setup = EcoVisionSetup()
    setup.run_setup()
