from sqlalchemy import Column, Integer, Float, Date, DateTime 
from datetime import datetime 
from app.database import Base 

class ProgressLog(Base): 
    __tablename__ = "progress_logs" 

    id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(Integer) 
    weight_kg = Column(Float) 
    logged_at = Column(Date) 
    created_at = Column(DateTime, default=datetime.utcnow)