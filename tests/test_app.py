import sqlite3

import pytest

from app import app, init_db


@pytest.fixture()
def client(tmp_path):
    app.config.update(TESTING=True, DATABASE=tmp_path / "test.db")
    with app.test_client() as test_client:
        with app.app_context():
            init_db()
        yield test_client


def test_task_lifecycle(client):
    response = client.post("/tasks", data={"title": "Write tests"})
    assert response.status_code == 302

    page = client.get("/")
    assert b"Write tests" in page.data

    with sqlite3.connect(app.config["DATABASE"]) as database:
        task_id = database.execute("SELECT id FROM tasks").fetchone()[0]

    response = client.post(f"/tasks/{task_id}/complete")
    assert response.status_code == 302
    assert b"is-complete" in client.get("/").data

    response = client.post(f"/tasks/{task_id}/delete")
    assert response.status_code == 302
    assert b"Write tests" not in client.get("/").data


def test_empty_task_is_ignored(client):
    client.post("/tasks", data={"title": "   "})
    assert b"No tasks yet" in client.get("/").data


def test_health_check_identifies_service(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "task-manager"}


def test_tasks_can_be_searched_and_filtered(client):
    client.post("/tasks", data={"title": "Plan release"})
    client.post("/tasks", data={"title": "Buy groceries"})

    with sqlite3.connect(app.config["DATABASE"]) as database:
        task_id = database.execute(
            "SELECT id FROM tasks WHERE title = ?", ("Plan release",)
        ).fetchone()[0]
    client.post(f"/tasks/{task_id}/complete")

    response = client.get("/?q=release&status=completed")

    assert b"Plan release" in response.data
    assert b"Buy groceries" not in response.data
