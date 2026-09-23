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