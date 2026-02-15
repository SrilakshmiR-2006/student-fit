from app.database import engine, Base 
from app.models import user, meal_plan, workout_plan, progress_log 
Base.metadata.create_all(bind=engine) 
print("Tables created.")