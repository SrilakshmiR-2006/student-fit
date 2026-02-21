from sqlalchemy import Column, Integer, String, Float, Text 
from app.database import Base 
class Workout(Base): 
    __tablename__ = "workouts" 
    id = Column(Integer, primary_key=True, index=True) 
    exercise_name = Column(String) 
    category = Column(String) 
    calories_burn_per_30min = Column(Float) 
    difficulty = Column(String) 
    goal = Column(String) 
    equipment_required = Column(String) 
    suggested_instructions = Column(Text, nullable=True)