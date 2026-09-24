import os
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DATABASE"] = Path(app.instance_path) / "tasks.db"


# -----------------------------------------------------------------------------
# Database helpers
# -----------------------------------------------------------------------------


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    database = get_db()
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    database.commit()


@app.teardown_appcontext
def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


# -----------------------------------------------------------------------------
# Web routes
# -----------------------------------------------------------------------------


@app.get("/")
def home():
    init_db()
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all")
    if status_filter not in {"all", "active", "completed"}:
        status_filter = "all"

    filters = []
    parameters = []
    if search_query:
        filters.append("LOWER(title) LIKE LOWER(?)")
        parameters.append(f"%{search_query}%")
    if status_filter == "active":
        filters.append("completed = 0")
    elif status_filter == "completed":
        filters.append("completed = 1")

    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    tasks = get_db().execute(
        "SELECT id, title, completed, created_at FROM tasks"
        f"{where_clause} ORDER BY completed, id DESC",
        parameters,
    ).fetchall()
    return render_template(
        "index.html",
        tasks=tasks,
        search_query=search_query,
        status_filter=status_filter,
    )


@app.post("/tasks")
def create_task():
    title = request.form.get("title", "").strip()
    if title:
        init_db()
        database = get_db()
        database.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        database.commit()
    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/complete")
def complete_task(task_id):
    init_db()
    database = get_db()
    database.execute(
        "UPDATE tasks SET completed = NOT completed WHERE id = ?", (task_id,)
    )
    database.commit()
    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    init_db()
    database = get_db()
    database.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    database.commit()
    return redirect(url_for("home"))


# -----------------------------------------------------------------------------
# Health check and application startup
# -----------------------------------------------------------------------------


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.config["DATABASE"] = Path(
        os.environ.get("TASK_DATABASE", app.config["DATABASE"])
    )
    with app.app_context():
        init_db()
    app.run(debug=True)