"""Health Companion – AI-powered meal and workout plans for students."""
import sys
from pathlib import Path

# Ensure project root is on path so "app" is the package (avoids "app is not a package" when run from app/)
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
from datetime import date
import pandas as pd

from app.database import SessionLocal
from app.config import GEMINI_API_KEY, DATABASE_URL
from app.services.user_service import get_user_by_id, create_user
from app.services.meal_plan_service import get_latest_meal_plan
from app.services.workout_plan_service import get_latest_workout_plan
from app.services.progress_service import log_weight, get_weight_logs
from app.ai_engine.calorie_engine import get_all_metrics
from app.ai_engine.meal_plan_generator import generate_and_save_meal_plan
from app.ai_engine.workout_plan_generator import generate_and_save_workout_plan
from app.models.recipes import Recipe

# Must be first Streamlit command
st.set_page_config(
    page_title="Health Companion",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state defaults
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "Profile"
if "latest_meal_plan" not in st.session_state:
    st.session_state["latest_meal_plan"] = None
if "latest_workout_plan" not in st.session_state:
    st.session_state["latest_workout_plan"] = None


def get_db_session():
    """Get a DB session and ensure it's closed after use."""
    return SessionLocal()


def check_env():
    """Return None if OK, else error message."""
    if not DATABASE_URL:
        return "Database not configured. Check your .env file (DATABASE_URL)."
    if not GEMINI_API_KEY:
        return "Gemini API key not found. Add GEMINI_API_KEY to your .env file."
    return None


# ----- Sidebar -----
with st.sidebar:
    st.title("Health Companion")
    st.caption("AI-powered meal and workout plans for students.")
    page = st.radio(
        "Go to",
        ["Profile", "Nutrition & Meals", "Workout", "Progress"],
        label_visibility="collapsed",
    )
st.session_state["page"] = page

# ----- Environment check -----
env_error = check_env()
if env_error:
    st.error(env_error)
    st.stop()

# ----- Page content -----
if page == "Profile":
    st.header("Profile")
    st.caption("Enter your details to get personalized calorie targets and plans.")

    with st.form("profile_form"):
        name = st.text_input("Name", placeholder="Your name")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height_cm = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
        weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
        goal = st.selectbox(
            "Goal",
            ["Weight Loss", "Maintain Weight", "Muscle Gain"],
        )
        dietary_preference = st.selectbox("Dietary preference", ["Veg", "Non-veg", "Vegan"])
        budget = st.number_input("Weekly food budget (₹)", min_value=0.0, value=500.0, step=50.0)
        equipment = st.selectbox(
            "Equipment available",
            ["None", "Yoga Mat", "Dumbbells", "Treadmill", "Resistance Bands", "Gym Machine", "Full Gym"],
        )
        workout_minutes_per_day = st.number_input("Workout minutes per day", min_value=0, max_value=120, value=30)
        submitted = st.form_submit_button("Save profile")

    if submitted:
        if not name or not name.strip():
            st.warning("Please enter your name.")
        else:
            db = get_db_session()
            try:
                user = create_user(
                    db,
                    name=name.strip(),
                    age=int(age),
                    gender=gender,
                    height_cm=float(height_cm),
                    weight_kg=float(weight_kg),
                    goal=goal,
                    dietary_preference=dietary_preference,
                    budget=float(budget),
                    equipment=equipment,
                    workout_minutes_per_day=int(workout_minutes_per_day),
                )
                st.session_state["user_id"] = user.id
                st.success("Profile saved!")
            except Exception as e:
                st.error(f"Could not save profile: {e}")
            finally:
                db.close()

    # Show metrics if user exists
    user_id = st.session_state.get("user_id")
    if user_id:
        db = get_db_session()
        try:
            user = get_user_by_id(db, user_id)
            if user:
                metrics = get_all_metrics(user)
                st.subheader("Your metrics")
                st.caption("Daily calorie target is based on your goal.")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("BMI", metrics["bmi"])
                with c2:
                    st.metric("BMR (kcal/day)", int(metrics["bmr"]))
                with c3:
                    st.metric("TDEE (kcal/day)", int(metrics["tdee"]))
                with c4:
                    st.metric("Daily calorie target", int(metrics["calorie_target"]))
        finally:
            db.close()

elif page == "Nutrition & Meals":
    st.header("Nutrition & Meals")
    st.caption("Generate a 7-day meal plan tailored to your profile.")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.info("Please complete your profile first. Use the sidebar to go to **Profile**.")
        st.stop()

    def load_meal_plan_into_session(db):
        plan_obj = get_latest_meal_plan(db, user_id)
        if plan_obj and plan_obj.plan_json:
            import json
            st.session_state["latest_meal_plan"] = json.loads(plan_obj.plan_json)
        else:
            st.session_state["latest_meal_plan"] = None

    db = get_db_session()
    try:
        if st.session_state.get("latest_meal_plan") is None:
            load_meal_plan_into_session(db)

        if st.button("Generate my meal plan", type="primary") or st.button("Regenerate meal plan"):
            with st.spinner("Generating your meal plan…"):
                try:
                    plan = generate_and_save_meal_plan(db, user_id)
                    if plan:
                        st.session_state["latest_meal_plan"] = plan
                        st.success("Meal plan generated!")
                    else:
                        st.error("Could not generate plan. Please try again.")
                        st.caption("Possible causes: no recipes in the database, or the AI returned invalid data. Check that recipes are loaded (scripts/load_recipes) and your Gemini API key is set in .env.")
                except Exception as e:
                    err = str(e)
                    if "429" in err or "quota" in err.lower():
                        st.warning("Rate limit reached. Wait about a minute and try again. You can switch to gemini-2.5-flash-lite in app/ai_engine/gemini_client.py if needed.")
                    else:
                        st.error("Could not generate plan. Please try again.")
                    with st.expander("Error details (for debugging)"):
                        st.code(err)
        else:
            pass  # show existing plan below

        plan = st.session_state.get("latest_meal_plan")
        if not plan:
            st.info("Generate your first meal plan using the button above.")
        else:
            days = plan.get("days", [])
            st.subheader("Your 7-day plan")
            for d in days:
                day_num = d.get("day", 0)
                date_str = d.get("date", "")
                meals = d.get("meals", [])
                with st.expander(f"Day {day_num} — {date_str}"):
                    for m in meals:
                        st.write(f"**{m.get('meal_type', 'Meal')}:** {m.get('recipe_name', '')} ({m.get('calories', 0)} kcal)")

            cost = plan.get("total_weekly_cost", 0)
            st.metric("Weekly cost", f"₹{cost:.0f}")

            # Simple grocery list from recipe IDs in plan
            recipe_ids = set()
            for d in days:
                for m in d.get("meals", []):
                    rid = m.get("recipe_id")
                    if rid is not None:
                        recipe_ids.add(rid)
            if recipe_ids:
                recipes_in_plan = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
                ingredients_list = []
                for r in recipes_in_plan:
                    if getattr(r, "ingredients", None):
                        ingredients_list.append(r.ingredients)
                if ingredients_list:
                    with st.expander("Grocery list (from selected recipes)"):
                        st.text_area("Ingredients", "\n".join(ingredients_list), height=200, disabled=True)
    finally:
        db.close()

elif page == "Workout":
    st.header("Workout")
    st.caption("Generate a weekly workout plan based on your goal and equipment.")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.info("Please complete your profile first.")
        st.stop()

    def load_workout_plan_into_session(db):
        plan_obj = get_latest_workout_plan(db, user_id)
        if plan_obj and plan_obj.plan_json:
            import json
            st.session_state["latest_workout_plan"] = json.loads(plan_obj.plan_json)
        else:
            st.session_state["latest_workout_plan"] = None

    db = get_db_session()
    try:
        if st.session_state.get("latest_workout_plan") is None:
            load_workout_plan_into_session(db)

        if st.button("Generate my workout plan", type="primary") or st.button("Regenerate workout plan"):
            with st.spinner("Generating your workout plan…"):
                try:
                    plan = generate_and_save_workout_plan(db, user_id)
                    if plan:
                        st.session_state["latest_workout_plan"] = plan
                        st.success("Workout plan generated!")
                    else:
                        st.error("Could not generate workout plan. Please try again.")
                        st.caption("Check that workouts are loaded (scripts/load_workouts) and your Gemini API key is set in .env.")
                except Exception as e:
                    err = str(e)
                    if "429" in err or "quota" in err.lower():
                        st.warning("Rate limit reached. Wait about a minute and try again. You can switch to gemini-2.5-flash-lite in app/ai_engine/gemini_client.py if needed.")
                    else:
                        st.error("Could not generate workout plan. Please try again.")
                    with st.expander("Error details (for debugging)"):
                        st.code(err)

        plan = st.session_state.get("latest_workout_plan")
        if not plan:
            st.info("Generate your first workout plan using the button above.")
        else:
            st.subheader("Your weekly workout")
            for d in plan.get("days", []):
                day_num = d.get("day", 0)
                exercises = d.get("exercises", [])
                with st.expander(f"Day {day_num}"):
                    for ex in exercises:
                        name = ex.get("name", "")
                        duration = ex.get("duration_min", "")
                        instructions = ex.get("instructions", "")
                        st.write(f"**{name}** — {duration} min")
                        if instructions:
                            st.caption(instructions)
    finally:
        db.close()

elif page == "Progress":
    st.header("Progress")
    st.caption("Log your weight to track progress over time.")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.info("Please complete your profile first.")
        st.stop()

    db = get_db_session()
    try:
        with st.form("log_weight_form"):
            weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
            log_date = st.date_input("Date", value=date.today())
            if st.form_submit_button("Log weight"):
                try:
                    log_weight(db, user_id, weight_kg, log_date)
                    st.success("Weight logged!")
                except Exception as e:
                    st.error(f"Could not log weight: {e}")

        logs = get_weight_logs(db, user_id)
        if len(logs) < 2:
            st.info("Log your first weight to see the chart. Add at least 2 entries for a trend line.")
        else:
            df = pd.DataFrame([
                {"date": log.logged_at, "weight_kg": log.weight_kg}
                for log in logs
            ])
            df = df.set_index("date")
            st.line_chart(df)
    finally:
        db.close()