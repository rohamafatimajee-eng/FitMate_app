# pages/4_Dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import (
    get_workout_history, get_body_metrics, get_current_streak,
)

st.set_page_config(page_title="Dashboard — FitMate", page_icon="📊", layout="wide")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in first.")
    st.stop()

st.title("📊 Fitness Progress Dashboard")

history = get_workout_history(st.session_state.user_id, limit=500)
metrics = get_body_metrics(st.session_state.user_id)
streak = get_current_streak(st.session_state.user_id)

total = len(history)
completed = sum(1 for h in history if h["completed"])
rate = (completed / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔥 Current Streak", f"{streak} day{'s' if streak != 1 else ''}")
col2.metric("📋 Total Logged", total)
col3.metric("✅ Completed", completed)
col4.metric("📈 Completion", f"{rate:.0f}%")

if metrics:
    st.subheader("⚖️ Body Weight Over Time")
    df_w = pd.DataFrame(metrics)
    df_w["date"] = pd.to_datetime(df_w["date"])
    df_w = df_w.sort_values("date")

    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(df_w["date"], df_w["weight_kg"], marker="o", color="#2E86AB", linewidth=2)
    ax.fill_between(df_w["date"], df_w["weight_kg"], alpha=0.15, color="#2E86AB")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight (kg)")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No body metrics yet. Go to **Tracker → Body Metrics**.")

if history:
    st.subheader("📅 Daily Workout Volume")
    df_h = pd.DataFrame(history)
    df_h["date"] = pd.to_datetime(df_h["date"])
    daily = df_h.groupby("date").size().reset_index(name="count")

    fig2, ax2 = plt.subplots(figsize=(10, 3.5))
    ax2.bar(daily["date"], daily["count"], color="#A23B72", width=0.6)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Exercises")
    ax2.grid(True, alpha=0.3, axis="y")
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig2)

    st.subheader("🏋️ Top Exercises")
    top = df_h["exercise_name"].value_counts().head(10)
    st.bar_chart(top)
else:
    st.info("No workouts logged yet. Head to **Tracker** to begin.")