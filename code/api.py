"""
FeedWise Prototype - Flask API
---------------------------------
This is the shared backend that lets the two separate websites (drift.html
and feedwise.html) work together, exactly like the real product concept:
InstaKilogram is the platform, FeedWise is an independent layer sitting on top of it.

InstaKilogram calls this to get recommendations and log what the user "watched."
FeedWise polls this to read the current session state and render the
diversity gauge + explanation log -- it never talks to InstaKilogram directly,
only to this shared backend. That's the actual architecture of the pitch.

Run with:  python3 api.py
Then open drift.html and feedwise.html as two separate browser tabs.

Endpoints:
  GET  /api/recommend   -> next recommendation based on current session history
  POST /api/watch       -> body {"post_id": "..."} logs that post as watched
  GET  /api/state        -> current history, repetition score, and log (for FeedWise)
  POST /api/reset        -> clears the session
"""

import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from feedwise_engine import (
    get_dataset, get_next_recommendation, get_repetition_score, generate_insights, WINDOW_SIZE
)

app = Flask(__name__)
CORS(app)

@app.after_request
def add_no_cache_headers(response):
    # Without this, some browsers will silently serve a cached copy of a
    # GET response instead of hitting the server -- which looked exactly
    # like "the feed keeps repeating" even after the exclude fix.
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

ALL_POSTS = get_dataset("dataset.json")
POSTS_BY_ID = {p["id"]: p for p in ALL_POSTS}
AVAILABLE_CATEGORIES = sorted({p["category"] for p in ALL_POSTS})

# category -> sorted list of subtopics that actually exist in the dataset
TAXONOMY = {}
for p in ALL_POSTS:
    if "subtopic" in p:
        TAXONOMY.setdefault(p["category"], set()).add(p["subtopic"])
TAXONOMY = {cat: sorted(subs) for cat, subs in TAXONOMY.items()}

try:
    with open("thumbnail_map.json") as f:
        THUMBNAIL_MAP = json.load(f)
except FileNotFoundError:
    THUMBNAIL_MAP = {}

# Server-side session state (single demo user -- fine for a live pitch demo).
SESSION = {
    "history": [],   # list of watched post dicts, oldest first
    "log": [],       # list of {post, explanation, intervened, score} for every watch event
    "goals": [],     # categories the user picked during onboarding (can be multiple), or []
    "subtopics": [], # optional finer-grained picks within those categories (e.g. "Physics")
}


@app.route("/api/taxonomy", methods=["GET"])
def taxonomy():
    """Categories that support drilling into subtopics, and which subtopics
    actually exist in the dataset -- so the goal picker never offers a
    sub-interest with no content behind it."""
    return jsonify(TAXONOMY)


@app.route("/api/dataset", methods=["GET"])
def dataset():
    return jsonify(ALL_POSTS)


@app.route("/api/categories", methods=["GET"])
def categories():
    """The set of categories that actually exist in the dataset -- used to
    build the onboarding goal picker on FeedWise so it never offers a goal
    with no content behind it."""
    return jsonify(AVAILABLE_CATEGORIES)


@app.route("/api/set_goal", methods=["POST"])
def set_goal():
    """Called from FeedWise's onboarding screen. Accepts either a single
    {"goal": "X"} or multiple {"goals": ["X","Y"]}. Resets the session so
    the personalized feed starts clean."""
    body = request.get_json(force=True)
    goals = body.get("goals")
    if goals is None:
        single = body.get("goal")
        goals = [single] if single else []

    invalid = [g for g in goals if g not in AVAILABLE_CATEGORIES]
    if invalid:
        return jsonify({"error": f"unknown categories: {invalid}"}), 400

    subtopics = body.get("subtopics", [])
    valid_subs = {s for subs in TAXONOMY.values() for s in subs}
    subtopics = [s for s in subtopics if s in valid_subs]

    SESSION["goals"] = goals
    SESSION["subtopics"] = subtopics
    SESSION["history"] = []
    SESSION["log"] = []
    return jsonify({"ok": True, "goals": goals, "subtopics": subtopics})


@app.route("/api/thumbnail_map", methods=["GET"])
def thumbnail_map():
    """Served over HTTP (rather than drift.html trying to fetch the local
    JSON file directly) because most browsers block fetch() of local files
    when a page is opened straight from disk (file://). Going through the
    backend works regardless of how drift.html was opened."""
    return jsonify(THUMBNAIL_MAP)


@app.route("/api/recommend", methods=["GET"])
def recommend():
    """Returns the next recommendation given the current session history.
    Does NOT advance history -- that only happens on /api/watch.

    Accepts an optional ?exclude=id1,id2,id3 query param -- posts already
    shown on screen but not yet watched (e.g. preloaded feed cards below
    the current one). Without this, calling /api/recommend twice in a row
    before any watch happens returns the exact same top pick both times,
    since history hasn't changed -- exclude avoids that duplicate."""
    exclude_param = request.args.get("exclude", "")
    exclude_ids = {i for i in exclude_param.split(",") if i}

    if exclude_ids:
        candidate_posts = [p for p in ALL_POSTS if p["id"] not in exclude_ids]
    else:
        candidate_posts = ALL_POSTS

    result = get_next_recommendation(SESSION["history"], candidate_posts, goal_categories=SESSION["goals"], goal_subtopics=SESSION["subtopics"])
    return jsonify(result)


@app.route("/api/watch", methods=["POST"])
def watch():
    """InstaKilogram calls this when a post scrolls into view and counts as watched."""
    body = request.get_json(force=True)
    post_id = body.get("post_id")
    post = POSTS_BY_ID.get(post_id)
    if not post:
        return jsonify({"error": "unknown post_id"}), 400

    # recompute the recommendation result for logging purposes (explanation,
    # intervened flag, score) based on history BEFORE this watch
    result = get_next_recommendation(SESSION["history"], ALL_POSTS, goal_categories=SESSION["goals"], goal_subtopics=SESSION["subtopics"])

    SESSION["history"].append(post)
    SESSION["log"].append({
        "post_id": post["id"],
        "category": post["category"],
        "creator": post["creator"],
        "explanation": result["explanation"],
        "intervened": result["intervention_triggered"],
        "score": result["repetition_score"],
    })

    return jsonify({"ok": True})


@app.route("/api/state", methods=["GET"])
def state():
    """FeedWise polls this to render the gauge + log. It only ever reads
    from here -- it never talks to InstaKilogram directly."""
    recent_window = SESSION["history"][-WINDOW_SIZE:]
    score = get_repetition_score(recent_window)
    return jsonify({
        "repetition_score": score,
        "history_length": len(SESSION["history"]),
        "log": list(reversed(SESSION["log"][-50:])),  # most recent first
        "goals": SESSION["goals"], "subtopics": SESSION.get("subtopics", []),
    })


@app.route("/api/insights", methods=["GET"])
def insights():
    """Generates a written analysis of the session so far -- a real
    computed summary (top categories, diversity trend, intervention rate),
    not just a stat dump."""
    return jsonify(generate_insights(SESSION["log"], goal_categories=SESSION["goals"]))


@app.route("/api/wrapped", methods=["GET"])
def wrapped():
    """A 'Session Wrapped' style recap -- the shareable, personality-driven
    summary of a viewing session (top category, a playful 'scroller type'
    label, headline numbers). Built from the same real log data as insights,
    just framed for sharing rather than analysis."""
    log = SESSION["log"]
    from collections import Counter as _Counter

    if len(log) < 3:
        return jsonify({"ready": False})

    total = len(log)
    counts = _Counter(e["category"] for e in log)
    top_cat, top_count = counts.most_common(1)[0]
    top_share = round(top_count / total * 100)
    distinct = len(counts)
    interventions = sum(1 for e in log if e["intervened"])
    avg_score = round(sum(e["score"] for e in log) / total, 2)

    # a light-hearted "scroller archetype" derived from real behaviour
    if avg_score >= 0.7:
        persona = "The Explorer"
        persona_desc = "You keep your feed wide open — variety is your whole vibe."
    elif avg_score >= 0.45:
        persona = "The Balanced Viewer"
        persona_desc = "A healthy mix, with a few favourites you keep coming back to."
    elif top_share >= 60:
        persona = "The Deep Diver"
        persona_desc = f"When you find {top_cat}, you commit. Hard."
    else:
        persona = "The Rabbit-Holer"
        persona_desc = "Your feed narrows fast — FeedWise had to pull you back out."

    return jsonify({
        "ready": True,
        "top_category": top_cat,
        "top_share": top_share,
        "distinct_categories": distinct,
        "total_watched": total,
        "interventions": interventions,
        "avg_diversity": avg_score,
        "persona": persona,
        "persona_desc": persona_desc,
        "goals": SESSION["goals"], "subtopics": SESSION.get("subtopics", []),
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    SESSION["history"] = []
    SESSION["log"] = []
    SESSION["goals"] = []
    SESSION["subtopics"] = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
