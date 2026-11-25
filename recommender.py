# recommender.py
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_all_exercises, get_profile

CDN_BASE = "https://cdn.jsdelivr.net/gh/yuhonas/free-exercise-db@main/exercises/"


def build_exercise_text(ex):
    """Exercise ki saari info ko ek text string mein combine karo."""
    primary = json.loads(ex["primary_muscles"]) if ex["primary_muscles"] else []
    secondary = json.loads(ex["secondary_muscles"]) if ex["secondary_muscles"] else []
    return (
        f"{ex['name']} {ex['level'] or ''} {ex['equipment'] or ''} "
        f"{ex['category'] or ''} {' '.join(primary)} {' '.join(secondary)}"
    )


def get_image_urls(exercise):
    """Exercise ki image URLs return karo."""
    if not exercise.get("images"):
        return []
    try:
        paths = json.loads(exercise["images"])
    except (json.JSONDecodeError, TypeError):
        return []
    return [CDN_BASE + p for p in paths if p]


def recommend_exercises(user_id, top_n=10):
    """User ke profile se top exercises rank karo."""
    profile = get_profile(user_id)
    exercises = get_all_exercises()
    if not exercises:
        return []

    if not profile or not profile.get("goal"):
        return exercises[:top_n]

    targets = profile["target_body_parts"].split(",") if profile["target_body_parts"] else []
    equipment_pref = profile["equipment"].split(",") if profile["equipment"] else []
    user_text = (
        f"{profile['goal']} {profile['fitness_level']} "
        f"{' '.join(targets)} {' '.join(equipment_pref)}"
    )

    corpus = [build_exercise_text(ex) for ex in exercises] + [user_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    user_vec = tfidf_matrix[-1]
    ex_vecs = tfidf_matrix[:-1]
    similarities = cosine_similarity(user_vec, ex_vecs).flatten()

    scored = list(zip(exercises, similarities))
    scored.sort(key=lambda x: x[1], reverse=True)

    return [ex for ex, _ in scored[:top_n]]