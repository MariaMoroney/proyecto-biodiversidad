# schemas.py - Schemas para especies marinas
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
import re


class MarineSightingBase(BaseModel):
    species_name: str
    location: str
    latitude: float
    longitude: float
    sighting_date: datetime
    observer_name: str
    observer_email: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None


class MarineSightingCreate(MarineSightingBase):
    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitud debe estar entre -90 y 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitud debe estar entre -180 y 180')
        return v

    @validator('observer_email')
    def validate_email(cls, v):
        if v and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
            raise ValueError('Email inválido')
        return v


class RawMarineDataResponse(MarineSightingBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class CleanedMarineDataResponse(BaseModel):
    id: int
    species_name: str
    species_category: Optional[str]
    location: str
    latitude: float
    longitude: float
    sighting_date: datetime
    observer_name: str
    observer_email: Optional[str]
    description: Optional[str]
    photo_url: Optional[str]
    validation_status: str
    data_quality_score: Optional[float]
    processed_at: datetime

    class Config:
        orm_mode = True


class PipelineLogResponse(BaseModel):
    id: int
    execution_date: datetime
    records_extracted: int
    records_transformed: int
    records_loaded: int
    records_rejected: int
    execution_time_seconds: float
    status: str
    error_message: Optional[str]
    backup_files: Optional[str]

    class Config:
        orm_mode = True


class PipelineStatusResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    log_id: Optional[int] = None