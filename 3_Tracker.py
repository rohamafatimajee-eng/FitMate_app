# pages/3_Tracker.py
import streamlit as st
from datetime import date
from database import (
    get_today_workouts, log_workout, update_workout_completion,
    delete_workout_log, get_workout_history, log_body_metric,
)
from recommender import recommend_exercises, get_image_urls

st.set_page_config(page_title="Tracker — FitMate", page_icon="✅")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in first.")
    st.stop()

st.title("✅ Daily Workout Tracker")
today = str(date.today())

tab1, tab2, tab3 = st.tabs(["📌 Today's Checklist", "➕ Log a Workout", "⚖️ Body Metrics"])

# ---------------- Tab 1: Checklist ----------------
with tab1:
    st.subheader(f"Today — {today}")
    logs = get_today_workouts(st.session_state.user_id, today)

    if not logs:
        st.info("No workouts logged for today. Use the **Log a Workout** tab.")
    else:
        completed = sum(1 for log in logs if log["completed"])
        total = len(logs)
        st.progress(completed / total)
        st.caption(f"**{completed}/{total}** exercises completed")

        for log in logs:
            col1, col2 = st.columns([5, 1])
            with col1:
                checked = st.checkbox(
                    f"{log['exercise_name']} — {log['sets']} sets × {log['reps']} reps",
                    value=bool(log["completed"]),
                    key=f"check_{log['id']}"
                )
                if checked != bool(log["completed"]):
                    update_workout_completion(log["id"], checked)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{log['id']}", help="Delete"):
                    delete_workout_log(log["id"], st.session_state.user_id)
                    st.rerun()

# ---------------- Tab 2: Log a Workout ----------------
with tab2:
    st.subheader("Add an exercise to today's plan")
    recs = recommend_exercises(st.session_state.user_id, top_n=50)
    if not recs:
        st.warning("Run `python seed_exercises.py` first.")
    else:
        ex_map = {f"{ex['name']} ({ex['level'] or 'any'})": ex for ex in recs}
        selected_label = st.selectbox("Choose exercise", list(ex_map.keys()))
        selected_ex = ex_map[selected_label]

        urls = get_image_urls(selected_ex)
        if urls:
            st.image(urls[0], width=280, caption=selected_ex["name"])

        col1, col2 = st.columns(2)
        with col1:
            sets = st.number_input("Sets", 1, 20, 3)
        with col2:
            reps = st.number_input("Reps", 1, 100, 10)

        if st.button("➕ Add to Today's Workout", use_container_width=True):
            log_workout(st.session_state.user_id, selected_ex["id"], today, sets, reps)
            st.success(f"Added **{selected_ex['name']}**! Switch to the Checklist tab.")
            st.rerun()

    st.divider()
    st.subheader("Recent History")
    history = get_workout_history(st.session_state.user_id, limit=20)
    if history:
        import pandas as pd
        df = pd.DataFrame(history)[["date", "exercise_name", "sets", "reps", "completed"]]
        df["completed"] = df["completed"].map({1: "✅", 0: "⬜"})
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No history yet.")

# ---------------- Tab 3: Body Metrics ----------------
with tab3:
    st.subheader("Log Today's Body Weight")
    weight = st.number_input("Weight (kg)", 30.0, 300.0, 70.0, step=0.1)
    notes = st.text_input("Notes (optional)")
    if st.button("💾 Save Body Metric", use_container_width=True):
        log_body_metric(st.session_state.user_id, today, weight, notes)
        st.success("Saved!")
        st.rerun()