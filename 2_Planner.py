# pages/2_Planner.py
import streamlit as st
import json
from recommender import recommend_exercises, get_image_urls
from database import get_profile

st.set_page_config(page_title="Planner — FitMate", page_icon="📋")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in first.")
    st.stop()

st.title("📋 Your Personalized Workout Plan")

profile = get_profile(st.session_state.user_id)
if not profile or not profile.get("goal"):
    st.info("Please complete your **Profile** first so we can recommend exercises.")
    st.stop()

# Cache recommendations; invalidate on profile change
sig = f"{profile.get('goal')}_{profile.get('fitness_level')}_" \
      f"{profile.get('target_body_parts')}_{profile.get('equipment')}"
if st.session_state.get("rec_sig") != sig or "recommendations" not in st.session_state:
    st.session_state.recommendations = recommend_exercises(st.session_state.user_id, top_n=12)
    st.session_state.rec_sig = sig

recommendations = st.session_state.recommendations

if not recommendations:
    st.warning("No exercises found. Run `python seed_exercises.py` first.")
    st.stop()

st.success(
    f"Showing **{len(recommendations)}** exercises tuned to: "
    f"**{profile['goal'].replace('_', ' ').title()}** • "
    f"{profile['fitness_level'].title()} • "
    f"{profile['target_body_parts'].replace(',', ', ').title()}"
)

SETS_REPS = {
    "muscle_gain":       ("3–4", "8–12"),
    "strength":          ("4–5", "3–6"),
    "weight_management": ("2–3", "12–15"),
    "flexibility":       ("Hold", "30–60s"),
}

for ex in recommendations:
    with st.expander(f"🏋️ {ex['name']}  —  {ex['level'].title() if ex['level'] else 'N/A'}"):
        image_urls = get_image_urls(ex)
        if image_urls:
            cols = st.columns(min(len(image_urls), 3))
            for col, url in zip(cols, image_urls):
                with col:
                    st.image(url, use_container_width=True)
        else:
            st.caption("_(No demo images available.)_")

        st.divider()

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Equipment:** {ex['equipment'] or 'Bodyweight'}")
            primary = json.loads(ex["primary_muscles"]) if ex["primary_muscles"] else []
            secondary = json.loads(ex["secondary_muscles"]) if ex["secondary_muscles"] else []
            st.markdown(f"**Primary Muscles:** {', '.join(primary) or 'N/A'}")
            if secondary:
                st.markdown(f"**Secondary Muscles:** {', '.join(secondary)}")
            st.markdown(f"**Category:** {ex['category'] or 'N/A'}")
            st.markdown(f"**Mechanic:** {ex['mechanic'] or 'N/A'}")

            instructions = json.loads(ex["instructions"]) if ex["instructions"] else []
            st.markdown("**Step-by-Step Instructions:**")
            for i, step in enumerate(instructions, 1):
                st.markdown(f"{i}. {step}")

        with col2:
            sets, reps = SETS_REPS.get(profile["goal"], ("3", "10"))
            st.metric("Suggested Sets", sets)
            st.metric("Suggested Reps", reps)
            st.caption("Rest: 60–90s between sets")