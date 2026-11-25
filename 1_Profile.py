# pages/1_Profile.py
import streamlit as st
from database import get_profile, update_profile

st.set_page_config(page_title="Profile — FitMate", page_icon="👤")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in first.")
    st.stop()

st.title("👤 Your Fitness Profile")

profile = get_profile(st.session_state.user_id) or {}

GOALS = ["muscle_gain", "strength", "weight_management", "flexibility"]
GOAL_LABELS = {
    "muscle_gain": "💪 Muscle Building",
    "strength": "🏋️ Strength Training",
    "weight_management": "⚖️ Weight Management",
    "flexibility": "🧘 Flexibility & Mobility",
}
LEVELS = ["beginner", "intermediate", "expert"]
BODY_PARTS = ["chest", "back", "shoulders", "biceps", "triceps",
              "legs", "abs", "glutes", "full body"]
EQUIPMENT = ["body only", "dumbbell", "barbell", "kettlebells",
             "machine", "cable", "bands", "exercise ball"]

with st.form("profile_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", 10, 100, int(profile.get("age") or 25))
    with col2:
        height = st.number_input("Height (cm)", 100.0, 250.0,
                                 float(profile.get("height_cm") or 170.0))
    with col3:
        weight = st.number_input("Weight (kg)", 30.0, 300.0,
                                 float(profile.get("weight_kg") or 70.0))

    if height and weight:
        bmi = weight / ((height / 100) ** 2)
        category = ("Underweight" if bmi < 18.5 else
                    "Normal" if bmi < 25 else
                    "Overweight" if bmi < 30 else "Obese")
        st.metric("Your BMI", f"{bmi:.1f}  ({category})")

    st.divider()

    fitness_level = st.selectbox(
        "Fitness Level", LEVELS,
        index=LEVELS.index(profile.get("fitness_level") or "beginner")
    )

    goal = st.selectbox(
        "Primary Fitness Goal", GOALS,
        format_func=lambda x: GOAL_LABELS[x],
        index=GOALS.index(profile.get("goal") or "muscle_gain")
    )

    target_body_parts = st.multiselect(
        "Target Body Parts (choose 1–4)",
        BODY_PARTS,
        default=[x for x in (profile.get("target_body_parts") or "").split(",") if x] or ["chest", "back"]
    )

    equipment = st.multiselect(
        "Available Equipment",
        EQUIPMENT,
        default=[x for x in (profile.get("equipment") or "").split(",") if x] or ["body only"]
    )

    submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if submitted:
        if not target_body_parts:
            st.error("Please select at least one target body part.")
        elif not equipment:
            st.error("Please select at least one equipment type.")
        else:
            update_profile(st.session_state.user_id, age, height, weight,
                           fitness_level, goal, target_body_parts, equipment)
            st.success("✅ Profile saved! Head over to the **Planner** page.")