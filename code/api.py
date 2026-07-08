"""
FeedWise Prototype - Flask API
---------------------------------
This is the shared backend that lets the two separate websites (drift.html
and feedwise.html) work together, exactly like the real product concept:
Drift is the platform, FeedWise is an independent layer sitting on top of it.

Drift calls this to get recommendations and log what the user "watched."
FeedWise polls this to read the current session state and render the
diversity gauge + explanation log -- it never talks to Drift directly,
only to this shared backend. That's the actual architecture of the pitch.

Run with:  python3 api.py
Then open drift.html and feedwise.html as two separate browser tabs.

Endpoints:
  GET  /api/recommend   -> next recommendation based on current session history
  POST /api/watch       -> body {"post_id": "..."} logs that post as watched
  GET  /api/state        -> current history, repetition score, and log (for FeedWise)
  POST /api/reset        -> clears the session
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from feedwise_engine import get_dataset, get_next_recommendation, get_repetition_score, WINDOW_SIZE

app = Flask(__name__)
CORS(app)

ALL_POSTS = get_dataset("dataset.json")
POSTS_BY_ID = {p["id"]: p for p in ALL_POSTS}

# Server-side session state (single demo user -- fine for a live pitch demo).
SESSION = {
    "history": [],   # list of watched post dicts, oldest first
    "log": [],       # list of {post, explanation, intervened, score} for every watch event
}


@app.route("/api/dataset", methods=["GET"])
def dataset():
    return jsonify(ALL_POSTS)


@app.route("/api/recommend", methods=["GET"])
def recommend():
    """Returns the next recommendation given the current session history.
    Does NOT advance history -- that only happens on /api/watch."""
    result = get_next_recommendation(SESSION["history"], ALL_POSTS)
    return jsonify(result)


@app.route("/api/watch", methods=["POST"])
def watch():
    """Drift calls this when the user taps 'Watch this'."""
    body = request.get_json(force=True)
    post_id = body.get("post_id")
    post = POSTS_BY_ID.get(post_id)
    if not post:
        return jsonify({"error": "unknown post_id"}), 400

    # recompute the recommendation result for logging purposes (explanation,
    # intervened flag, score) based on history BEFORE this watch
    result = get_next_recommendation(SESSION["history"], ALL_POSTS)

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
    from here -- it never talks to Drift directly."""
    recent_window = SESSION["history"][-WINDOW_SIZE:]
    score = get_repetition_score(recent_window)
    return jsonify({
        "repetition_score": score,
        "history_length": len(SESSION["history"]),
        "log": list(reversed(SESSION["log"][-50:])),  # most recent first
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    SESSION["history"] = []
    SESSION["log"] = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)