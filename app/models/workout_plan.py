from sqlalchemy import Column, Integer, Text, DateTime 
from datetime import datetime 
from app.database import Base 

class WorkoutPlan(Base):
    __tablename__ = "workout_plans" 
    
    id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(Integer) 
    plan_json = Column(Text) 
    created_at = Column(DateTime, default=datetime.utcnow)