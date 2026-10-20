
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import database, review_history


@pytest.fixture
def test_client(tmp_path, monkeypatch):
    test_database = tmp_path / "test_codeguard.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    database.initialize_database()

    with TestClient(app) as client:
        yield client


def test_list_reviews_returns_empty_list(test_client):
    response = test_client.get("/reviews")

    assert response.status_code == 200
    assert response.json() == {"reviews": []}


def test_review_endpoint_saves_review_to_history(test_client):
    response = test_client.post(
        "/review",
        json={
            "language": "python",
            "code": "import os\nprint('hello')\n",
        },
    )

    assert response.status_code == 200

    history_response = test_client.get("/reviews")

    assert history_response.status_code == 200
    reviews = history_response.json()["reviews"]

    assert len(reviews) == 1
    assert reviews[0]["language"] == "python"
    assert reviews[0]["status"] == "completed"


def test_get_saved_review_returns_code_and_findings(test_client):
    code = "import os\nprint('hello')\n"

    test_client.post(
        "/review",
        json={"language": "python", "code": code},
    )

    history_response = test_client.get("/reviews")
    review_id = history_response.json()["reviews"][0]["id"]

    response = test_client.get(f"/reviews/{review_id}")

    assert response.status_code == 200

    saved = response.json()
    assert saved["id"] == review_id
    assert saved["language"] == "python"
    assert saved["code"] == code
    assert isinstance(saved["findings"], list)
    assert "ai_review" in saved


def test_missing_review_returns_404(test_client):
    response = test_client.get("/reviews/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found."


def test_history_limit_is_respected(test_client):
    for index in range(3):
        review_history.save_review(
            language="python",
            code=f"print({index})",
            status="completed",
            findings=[],
            ai_review=None,
        )

    response = test_client.get("/reviews?limit=2")

    assert response.status_code == 200
    assert len(response.json()["reviews"]) == 2


def test_history_limit_is_capped_at_100(test_client):
    for index in range(101):
        review_history.save_review(
            language="python",
            code=f"print({index})",
            status="completed",
            findings=[],
            ai_review=None,
        )

    response = test_client.get("/reviews?limit=500")

    assert response.status_code == 200
    assert len(response.json()["reviews"]) == 100
    
def test_history_limit_below_minimum_is_clamped(test_client):
    response = test_client.get("/reviews?limit=0")

    assert response.status_code == 200
    assert len(response.json()["reviews"]) <= 1


def test_history_limit_above_maximum_is_capped(test_client):
    for index in range(101):
        review_history.save_review(
            language="python",
            code=f"print({index})",
            status="completed",
            findings=[],
            ai_review=None,
        )

    response = test_client.get("/reviews?limit=500")

    assert response.status_code == 200
    assert len(response.json()["reviews"]) == 100