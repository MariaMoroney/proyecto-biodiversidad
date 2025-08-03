from sqlalchemy.orm import Session
from . import models

def get_all_cleaned_data(db: Session):
    return db.query(models.CleanedData).all()