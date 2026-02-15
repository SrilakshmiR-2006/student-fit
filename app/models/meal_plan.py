from sqlalchemy import Column, Integer, String, Float, DateTime, Text 
from datetime import datetime 
from app.database import Base 

class MealPlan(Base): 
    __tablename__ = "meal_plans" 
    
    id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(Integer) 
    calorie_target = Column(Float)
    plan_json = Column(Text)
    weekly_cost = Column(Float) 
    created_at = Column(DateTime, default=datetime.utcnow)