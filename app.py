"""
Northfield Operations Desk — Flask backend.

Serves the dashboard frontend and a small JSON API backed by an in-memory
data store. Swap `DATA` for a real database (Postgres, SQLite, etc.) when
you're ready to use real numbers.
"""

from datetime import date

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Fake / placeholder data — replace this with real queries later.
# ---------------------------------------------------------------------------

DATA = {
    "company": {
        "name": "Northfield",
        "tagline": "Operations Desk",
        "stats": {"projects": 23, "teams": 5, "people": 42},
    },
    "kpis": [
        {"label": "Revenue pipeline", "value": "$482K", "delta": "+12% ($51K)", "trend": "up"},
        {"label": "Team utilization", "value": "84%", "delta": "-3 pts", "trend": "down"},
        {"label": "Client NPS", "value": "62", "delta": "+5 pts", "trend": "up"},
        {"label": "Open tickets", "value": "18", "delta": "-4 (good)", "trend": "up"},
        {"label": "On-time delivery", "value": "91%", "delta": "no change", "trend": "flat"},
    ],
    "calendar": [
        {"day": "Mon", "date": 14, "events": [
            {"time": "10:00", "title": "Sprint planning", "team": "eng"},
            {"time": "2:00", "title": "Call: Bracken Co.", "team": "sales"},
        ]},
        {"day": "Tue", "date": 15, "events": [
            {"time": "11:00", "title": "Aster design review", "team": "design"},
            {"time": "4:30", "title": "All-hands prep", "team": "all"},
        ]},
        {"day": "Wed", "date": 16, "events": [
            {"time": "9:30", "title": "Aster deck sign-off", "team": "design"},
            {"time": "1:00", "title": "API cutover window", "team": "eng"},
            {"time": "3:00", "title": "Renewal: Marlowe Ltd.", "team": "sales"},
        ]},
        {"day": "Thu", "date": 17, "events": [
            {"time": "10:00", "title": "Renewal: Union Bank", "team": "sales"},
            {"time": "2:00", "title": "Monthly all-hands", "team": "all"},
        ]},
        {"day": "Fri", "date": 18, "events": [
            {"time": "11:00", "title": "Retro + demo", "team": "eng"},
            {"time": "4:00", "title": "Friday wrap", "team": "all"},
        ]},
    ],
    "today": "Wed",
    "tasks": [
        {"id": "t1", "title": "Finalize Aster rebrand deck for client sign-off", "owner": "M. Reyes", "priority": "high", "done": False},
        {"id": "t2", "title": "Ship API migration to staging", "owner": "D. Okafor", "priority": "high", "done": True},
        {"id": "t3", "title": "Prep renewal materials for Marlowe Ltd.", "owner": "S. Patel", "priority": "high", "done": False},
        {"id": "t4", "title": "Fix billing sync bug (blocking support queue)", "owner": "D. Okafor", "priority": "high", "done": False},
        {"id": "t5", "title": "Draft Q4 case study copy", "owner": "L. Novak", "priority": "med", "done": True},
        {"id": "t6", "title": "Review Union Bank contract redlines", "owner": "S. Patel", "priority": "med", "done": False},
        {"id": "t7", "title": "Update onboarding template for new hires", "owner": "J. Kim", "priority": "low", "done": True},
        {"id": "t8", "title": "Book venue for monthly all-hands", "owner": "J. Kim", "priority": "low", "done": True},
        {"id": "t9", "title": "Tag and archive closed Q3 tickets", "owner": "R. Alva", "priority": "med", "done": False},
    ],
    "teams": [
        {
            "name": "Design", "status": "atrisk", "headcount": 6, "capacity": 92,
            "focus": "Finishing the Aster rebrand deck; waiting on client asset delivery.",
        },
        {
            "name": "Engineering", "status": "ontrack", "headcount": 11, "capacity": 78,
            "focus": "API migration cutover scheduled Wednesday afternoon.",
        },
        {
            "name": "Sales", "status": "ontrack", "headcount": 7, "capacity": 65,
            "focus": "Two renewals in motion this week, pipeline ahead of target.",
        },
        {
            "name": "Support", "status": "blocked", "headcount": 5, "capacity": 88,
            "focus": "Waiting on eng fix for the billing sync bug before tickets can close.",
        },
        {
            "name": "Marketing", "status": "ontrack", "headcount": 4, "capacity": 54,
            "focus": "Q4 case study campaign drafted, review scheduled Friday.",
        },
    ],
}


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.route("/api/overview")
def api_overview():
    """Everything the dashboard needs for first paint, in one call."""
    return jsonify({
        "company": DATA["company"],
        "kpis": DATA["kpis"],
        "calendar": DATA["calendar"],
        "today": DATA["today"],
        "teams": DATA["teams"],
        "today_label": date.today().strftime("%A, %B %-d"),
    })


@app.route("/api/kpis")
def api_kpis():
    return jsonify(DATA["kpis"])


@app.route("/api/calendar")
def api_calendar():
    return jsonify({"today": DATA["today"], "days": DATA["calendar"]})


@app.route("/api/teams")
def api_teams():
    return jsonify(DATA["teams"])


@app.route("/api/tasks", methods=["GET"])
def api_tasks_list():
    return jsonify(DATA["tasks"])


@app.route("/api/tasks", methods=["POST"])
def api_tasks_create():
    body = request.get_json(force=True) or {}
    title = (body.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    new_task = {
        "id": f"t{len(DATA['tasks']) + 1}-{abs(hash(title)) % 1000}",
        "title": title,
        "owner": body.get("owner", "Unassigned"),
        "priority": body.get("priority", "med"),
        "done": False,
    }
    DATA["tasks"].append(new_task)
    return jsonify(new_task), 201


@app.route("/api/tasks/<task_id>/toggle", methods=["POST"])
def api_tasks_toggle(task_id):
    for task in DATA["tasks"]:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            return jsonify(task)
    return jsonify({"error": "task not found"}), 404


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def api_tasks_delete(task_id):
    before = len(DATA["tasks"])
    DATA["tasks"] = [t for t in DATA["tasks"] if t["id"] != task_id]
    if len(DATA["tasks"]) == before:
        return jsonify({"error": "task not found"}), 404
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
