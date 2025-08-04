#!/bin/bash
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
