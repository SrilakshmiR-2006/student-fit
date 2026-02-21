from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String)  
    age = Column(Integer) 
    gender = Column(String) 
    height_cm = Column(Float) 
    weight_kg = Column(Float) 
    goal = Column(String) 
    dietary_preference = Column(String) 
    budget = Column(Float) 
    equipment = Column(String) 
    workout_minutes_per_day = Column(Integer) 
    created_at = Column(DateTime, default=datetime.utcnow)