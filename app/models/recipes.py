from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    calories_per_serving = Column(Float)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    diet_type = Column(String)
    cost_per_serving = Column(Float)
    cuisine = Column(String, nullable=True)
    meal_type = Column(String, nullable=True)  # Breakfast, Lunch, Dinner, etc.
    # Full recipe details (PDF plan doesn't include these; added for full recipe display & grocery list)
    ingredients = Column(Text, nullable=True)   # e.g. "rice, dal, turmeric" or one per line
    instructions = Column(Text, nullable=True)   # method / steps (plain text or numbered)