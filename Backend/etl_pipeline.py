#pipeline completo checado
import os
import json
import csv
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import re
import math

#importar modelos
from database import SessionLocal, engine
from models import RawMarineData, CleanedMarineData, PipelineLog

class BiodiversityETLPipeline:
    """Pipeline ETL"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        self.db = SessionLocal()
        
        #metricas
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'records_extracted': 0,
            'records_transformed': 0,
            'records_loaded': 0,
            'records_rejected': 0,
            'errors': [],
            'backup_files': []
        }

        
        #acá se configura la validación
        self.costa_rica_bounds = {
            'lat_min': 8.0, 'lat_max': 11.5,
            'lng_min': -87.0, 'lng_max': -82.5
        }
        
        self.valid_categories = {
            'birds': ['ave', 'bird', 'pájaro', 'quetzal', 'tucán', 'colibrí'],
            'mammals': ['mamífero', 'mammal', 'mono', 'perezoso', 'jaguar', 'puma'],
            'reptiles': ['reptil', 'reptile', 'iguana', 'serpiente', 'tortuga'],
            'amphibians': ['anfibio', 'amphibian', 'rana', 'sapo']
        }
        
        self.conservation_status_map = {
            'estable': 'stable',
            'vulnerable': 'vulnerable',
            'en peligro': 'endangered',
            'crítico': 'critical',
            'stable': 'stable',
            'endangered': 'endangered',
            'critical': 'critical'
        }

    def setup_logging(self):
        """sistema de logging"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_dir}/pipeline_log_{timestamp}.json"
        
        #config del loggin
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{log_dir}/pipeline_{timestamp}.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file



    def setup_directories(self):
        """directorios"""
        directories = ["backups/raw", "backups/cleaned", "logs", "temp"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def extract_data(self) -> List[Dict]:
        """
        extract
        """
        self.logger.info("↻ Iniciando extracción de datos...")
        self.metrics['start_time'] = datetime.now()
        
        try:
            #extrae los datos de la tabla raw
            raw_data = self.db.query(RawMarineData).all()
            
            #y se convierten a diccionario 
            extracted_records = []
            for record in raw_data:
                extracted_records.append({
                    'id': record.id,
                    'species_name': record.species_name,
                    'location': record.location,
                    'latitude': record.latitude,
                    'longitude': record.longitude,
                    'sighting_date': record.sighting_date,
                    'observer_name': record.observer_name,
                    'observer_email': record.observer_email,
                    'description': record.description,
                    'photo_url': record.photo_url,
                    'created_at': record.created_at
                })
            
            self.metrics['records_extracted'] = len(extracted_records)
            self.logger.info(f"ꪜ Extraídos {len(extracted_records)} registros de la tabla RAW")
            
            #backup de datos
            self.create_backup(extracted_records, 'raw')
            
            return extracted_records
            
        except Exception as e:
            error_msg = f"Error de extracción: {str(e)}"
            self.logger.error(error_msg)
            self.metrics['errors'].append(error_msg)
            return []

    def transform_data(self, raw_records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        transform
        """
        self.logger.info("↻ Iniciando transformación de datos...")
        
        cleaned_records = []
        rejected_records = []
        
        for record in raw_records:
            try:
                #transformaciones
                transformed_record= self.clean_record(record)
                
                if transformed_record:
                    #validar nuevo registro
                    if self.validate_record(transformed_record):
                        #score de calidad
                        transformed_record['data_quality_score'] = self.calculate_quality_score(transformed_record)
                        cleaned_records.append(transformed_record)
                    else:
                        rejected_records.append({**record, 'rejection_reason': 'Validación fallida'})
                else:
                    rejected_records.append({**record, 'rejection_reason': 'Transformación fallida'})
                    
            except Exception as e:
                error_msg = f"Error trans. el registro {record.get('id', 'unknown')}: {str(e)}"
                self.logger.warning(error_msg)
                rejected_records.append({**record, 'rejection_reason': error_msg})
        
        self.metrics['records_transformed'] = len(cleaned_records)
        self.metrics['records_rejected'] = len(rejected_records)
        
        self.logger.info(f"ꪜ Transformados {len(cleaned_records)} registros")
        self.logger.info(f"✖ Rechazados {len(rejected_records)} registros")
        
        return cleaned_records, rejected_records

    def clean_record(self, record: Dict) -> Optional[Dict]:
        """Limpiar registros individuales"""
        try:
            cleaned = {}
            
            #limp nombre
            species_name = str(record.get('species_name', '')).strip()
            if not species_name or species_name.lower() in ['null', 'none', '']:
                return None
            
            cleaned['species_name'] = self.normalize_name(species_name)
            cleaned['species_category'] = self.categorize_species(species_name)
            
            #limp ubicación
            location = str(record.get('location', '')).strip()
            cleaned['location'] = location if location else 'Ubicación desconocida'
            
            #limp y validar coordenadas
            try:
                lat = float(record.get('latitude', 0))
                lng = float(record.get('longitude', 0))
                
                #que esten las coor en costa rica
                if self.is_cr_coords(lat, lng):
                    cleaned['latitude'] = round(lat, 6)
                    cleaned['longitude'] = round(lng, 6)
                else:
                    return None
                    
            except (ValueError, TypeError):
                return None
            
            #limp fecha
            sighting_date = record.get('sighting_date')
            if isinstance(sighting_date, str):
                try:
                    sighting_date = datetime.fromisoformat(sighting_date.replace('Z', '+00:00'))
                except:
                    sighting_date = datetime.now()
            
            cleaned['sighting_date'] = sighting_date
            
            #limp observador nombre
            observer_name = str(record.get('observer_name', '')).strip()
            cleaned['observer_name'] = observer_name if observer_name else 'Anónimo'
            
            #limp mail
            observer_email = record.get('observer_email')
            if observer_email and self.is_valid_email(observer_email):
                cleaned['observer_email'] = observer_email.lower().strip()
            else:
                cleaned['observer_email'] = None
            
            #limp descrip
            description = record.get('description')
            if description:
                cleaned['description'] = str(description).strip()[:1000]  # Limitar longitud
            else:
                cleaned['description'] = None
            
            #limo url de foto
            photo_url = record.get('photo_url')
            if photo_url and self.is_valid_url(photo_url):
                cleaned['photo_url'] = photo_url.strip()
            else:
                cleaned['photo_url'] = None
            
            #resto de campos
            cleaned['validation_status'] = 'pending'
            cleaned['processed_at'] = datetime.now()
            
            return cleaned
            
        except Exception as e:
            self.logger.warning(f"Error limpiando registro: {str(e)}")
            return None

    def normalize_name(self, species_name: str) -> str:
        """normalizar el nombre de las especies"""
        #convertir el titulo y limpiar espacios extra
        normalized = ' '.join(species_name.strip().split())
        
        #normalizaciones más comunes (estas fueron a juicio personal)
        normalizations = {
            'quetzal resplandeciente': 'Quetzal Resplandeciente',
            'perezoso de tres dedos': 'Perezoso de Tres Dedos',
            'iguana verde': 'Iguana Verde',
            'tucan pico iris': 'Tucán Pico Iris',
            'mono aullador': 'Mono Aullador',
            'rana venenosa': 'Rana Venenosa',
            'colibri garganta rubi': 'Colibrí Garganta Rubí',
            'jaguar': 'Jaguar'
        }
        
        normalized_lower = normalized.lower()
        return normalizations.get(normalized_lower, normalized.title())

    def categorize_species(self, species_name: str) -> str:
        """categorizar especies auto"""
        species_lower = species_name.lower()
        
        for category, keywords in self.valid_categories.items():
            for keyword in keywords:
                if keyword in species_lower:
                    return category
        
        return 'unknown'

    def is_cr_coords(self, lat: float, lng: float) -> bool:
        """(comentado antes) valida que las coordenadas esten en CR"""
        return (self.costa_rica_bounds['lat_min'] <= lat <= self.costa_rica_bounds['lat_max'] and
                self.costa_rica_bounds['lng_min'] <= lng <= self.costa_rica_bounds['lng_max'])

    def is_valid_email(self, email: str) -> bool:
        """val el formato del mail"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def is_valid_url(self, url: str) -> bool:
        """val formato de URL"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None

    def validate_record(self, record: Dict) -> bool:
        """val los registro  que se transformaron"""
        required_fields = ['species_name', 'location', 'latitude', 'longitude', 'sighting_date', 'observer_name']
        
        for field in required_fields:
            if not record.get(field):
                return False
        
        #extra validaciones
        if not isinstance(record['latitude'], (int, float)):
            return False
        if not isinstance(record['longitude'], (int, float)):
            return False
        if not isinstance(record['sighting_date'], datetime):
            return False
            
        return True

    def calculate_quality_score(self, record: Dict) -> float:
        """calcular los scores de calidad"""
        score = 0.0
        max_score = 10.0
        
        #nombre de la especie +2
        if record.get('species_name') and len(record['species_name']) > 3:
            score += 2.0
        
        #coords validad +2
        if (record.get('latitude') and record.get('longitude') and 
            self.is_cr_coords(record['latitude'], record['longitude'])):
            score += 2.0
        
        #observador identificado +1
        if record.get('observer_name') and record['observer_name'] != 'Anónimo':
            score += 1.0
        
        #mail valido +1
        if record.get('observer_email'):
            score += 1.0
        
        #hay una descripcion +1
        if record.get('description') and len(record['description']) > 10:
            score += 1.0
        
        #hay una foto +1
        if record.get('photo_url'):
            score += 1.0
        
        #la fecha es reciente +1
        if record.get('sighting_date'):
            days_ago = (datetime.now() - record['sighting_date']).days
            if days_ago <= 30:
                score += 1.0
        
        #la categoría su esta en los records +1
        if record.get('species_category') and record['species_category'] != 'unknown':
            score += 1.0
        
        return round(score / max_score, 2)



    def load_data(self, cleaned_records: List[Dict]) -> int:
        """
        load, los datos limpios
        """
        self.logger.info("↻ Iniciando carga de datos...")
        
        loaded_count = 0
        
        try:
            for record in cleaned_records:
                #nuevo registro con los datos limpios
                cleaned_data = CleanedMarineData(
                    species_name=record['species_name'],
                    species_category=record['species_category'],
                    location=record['location'],
                    latitude=record['latitude'],
                    longitude=record['longitude'],
                    sighting_date=record['sighting_date'],
                    observer_name=record['observer_name'],
                    observer_email=record['observer_email'],
                    description=record['description'],
                    photo_url=record['photo_url'],
                    validation_status=record['validation_status'],
                    data_quality_score=record['data_quality_score'],
                    processed_at=record['processed_at']
                )
                
                self.db.add(cleaned_data)
                loaded_count += 1
            
            self.db.commit()
            
            self.metrics['records_loaded'] = loaded_count
            self.logger.info(f"ꪜ Cargados {loaded_count} registros a tabla limpia")
            
            #backup
            self.create_backup(cleaned_records, 'cleaned')
            
            return loaded_count
            
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error en carga: {str(e)}"
            self.logger.error(error_msg)
            self.metrics['errors'].append(error_msg)
            return 0


    def create_backup(self, data: List[Dict], data_type: str):
        """Crear backup con timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/{data_type}/biodiversity_{data_type}_{timestamp}.csv"
        
        try:
            if data:
                df = pd.DataFrame(data)
                df.to_csv(backup_file, index=False, encoding='utf-8')
                
                backup_info = {
                    'type': data_type,
                    'filename': os.path.basename(backup_file),
                    'path': backup_file,
                    'size': f"{os.path.getsize(backup_file) / 1024:.1f} KB",
                    'records': len(data),
                    'timestamp': timestamp
                }
                
                self.metrics['backup_files'].append(backup_info)
                self.logger.info(f"Backup creado: {backup_file}")
            
        except Exception as e:
            error_msg = f"Error creando backup: {str(e)}"
            self.logger.warning(error_msg)
            self.metrics['errors'].append(error_msg)

    def log_pipeline_execution(self):
        """ejecutar el pipeline en la base de datos"""
        try:
            self.metrics['end_time'] = datetime.now()
            execution_time = (self.metrics['end_time'] - self.metrics['start_time']).total_seconds()
            

            #status
            status = 'success'
            if self.metrics['errors']:
                status = 'warning' if self.metrics['records_loaded'] > 0 else 'error'
            
            #log de los datos
            pipeline_log = PipelineLog(
                execution_date=self.metrics['start_time'],
                records_extracted=self.metrics['records_extracted'],
                records_transformed=self.metrics['records_transformed'],
                records_loaded=self.metrics['records_loaded'],
                records_rejected=self.metrics['records_rejected'],
                execution_time_seconds=execution_time,
                status=status,
                error_message='; '.join(self.metrics['errors']) if self.metrics['errors'] else None,
                backup_files=json.dumps(self.metrics['backup_files'])
            )
            
            self.db.add(pipeline_log)
            self.db.commit()
            


            #aqui lo mismo pero detallado y en json
            detailed_log = {
                'pipeline_execution': {
                    'start_time': self.metrics['start_time'].isoformat(),
                    'end_time': self.metrics['end_time'].isoformat(),
                    'execution_time_seconds': execution_time,
                    'status': status
                },
                'metrics': self.metrics,
                'backup_files': self.metrics['backup_files'],
                'errors': self.metrics['errors']
            }
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_log, f, indent=2, default=str)
            
            self.logger.info(f"Log guardado: {self.log_file}")
            
        except Exception as e:
            self.logger.error(f"Error registrando ejecución: {str(e)}")

    def run_etl(self) -> Dict:
        """ejecutar pipeline completo"""
        self.logger.info("Iniciando pipeline ETL de Biodiversidad")
        
        try:
            # extract:
            raw_data = self.extract_data()
            if not raw_data:
                self.logger.warning("D: No hay datos para procesar")
                return self.get_execution_summary()
            
            # transform:
            cleaned_data, rejected_data = self.transform_data(raw_data)
            
            # loading
            if cleaned_data:
                self.load_data(cleaned_data)
            
            # LOGG
            self.log_pipeline_execution()
            
            summary = self.get_execution_summary()
            self.logger.info("ꪜ Pipeline ETL completado exitosamente!!")
            
            return summary
            
        except Exception as e:
            error_msg = f"Error crítico en pipeline: {str(e)}"
            self.logger.error(error_msg)
            self.metrics['errors'].append(error_msg)
            return self.get_execution_summary()
        
        finally:
            self.db.close()



    def get_execution_summary(self) -> Dict:
        """resumen de la ejecucion"""
        if self.metrics['end_time'] is None:
            self.metrics['end_time'] = datetime.now()
        
        if self.metrics['start_time'] is None:
            execution_time = 0
        else:
            execution_time = (self.metrics['end_time'] - self.metrics['start_time']).total_seconds()
        
        return {
            'status': 'success' if not self.metrics['errors'] else 'error',
            'timestamp': self.metrics['end_time'].isoformat(),
            'execution_time_seconds': round(execution_time, 2),
            'records_extracted': self.metrics['records_extracted'],
            'records_transformed': self.metrics['records_transformed'],
            'records_loaded': self.metrics['records_loaded'],
            'records_rejected': self.metrics['records_rejected'],
            'data_quality_score': round(
                (self.metrics['records_loaded'] / max(self.metrics['records_extracted'], 1)) * 100, 1
            ),
            'backup_files': self.metrics['backup_files'],
            'errors': self.metrics['errors'],
            'log_file': self.log_file
        }


# funcion principal: (ejecutar el pipeline)
def run_etl() -> Dict:
    pipeline = BiodiversityETLPipeline()
    return pipeline.run_etl()


#incertar los datos de prieba raw
def insert_sample_data():
    db = SessionLocal()
    
    sample_data = [
        {
            'species_name': 'Quetzal Resplandeciente',
            'location': 'Monteverde, Costa Rica',
            'latitude': 10.3009,
            'longitude': -84.8066,
            'sighting_date': datetime.now() - timedelta(days=1),
            'observer_name': 'Ana García',
            'observer_email': 'ana.garcia@email.com',
            'description': 'Avistamiento de quetzal macho con plumaje completo',
            'photo_url': 'https://example.com/quetzal.jpg'
        },
        {
            'species_name': 'perezoso tres dedos',  #sin normalizar
            'location': 'Manuel Antonio',
            'latitude': 9.3847,
            'longitude': -84.1506,
            'sighting_date': datetime.now() - timedelta(days=2),
            'observer_name': 'Carlos Méndez',
            'observer_email': 'carlos@invalid-email',  #mail inv
            'description': 'Perezoso descansando en cecropia',
            'photo_url': None
        },
        {
            'species_name': '',  # nom vacio
            'location': 'Corcovado',
            'latitude': 8.5367,
            'longitude': -83.5914,
            'sighting_date': datetime.now(),
            'observer_name': 'María Rodríguez',
            'observer_email': 'maria.rodriguez@email.com',
            'description': 'Avistamiento nocturno',
            'photo_url': 'https://example.com/unknown.jpg'
        },
        {
            'species_name': 'Jaguar',
            'location': 'Parque Nacional Corcovado',
            'latitude': 8.5367,
            'longitude': -83.5914,
            'sighting_date': datetime.now() - timedelta(hours=6),
            'observer_name': 'Roberto Silva',
            'observer_email': 'roberto.silva@conservation.org',
            'description': 'Jaguar adulto cruzando sendero principal',
            'photo_url': 'https://example.com/jaguar.jpg'
        }
    ]
    
    try:
        for data in sample_data:
            raw_record = RawMarineData(**data)
            db.add(raw_record)
        
        db.commit()
        print(f"Insertados {len(sample_data)} registros de prueba en tabla RAW")
        
    except Exception as e:
        db.rollback()
        print(f" Error de prueba: {str(e)}")
    
    finally:
        db.close()


if __name__ == "__main__":
    #realizar prueba
    print("Insertando datos de prueba...")
    insert_sample_data()
    
    #se ejecuta el pipeline
    print("\\n🚀 Ejecutando pipeline ETL...")
    result = run_etl()
    
    print("\\nResumen de ejecución:")
    print(json.dumps(result, indent=2, default=str))
