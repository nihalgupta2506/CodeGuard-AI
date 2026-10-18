
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_python_review_returns_structured_findings():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "import os\nprint('hello')\n",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["language"] == "python"
    assert data["status"] == "completed"
    assert data["analyzer"]["name"] == "Ruff"
    assert data["findings_count"] == len(data["findings"])
    assert any(
        finding["rule_id"] == "F401"
        for finding in data["findings"]
    )


def test_clean_python_code():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "def add(a, b):\n    return a + b\n",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["findings"] == []
    assert data["findings_count"] == 0


def test_cpp_analyzer_is_reported_unavailable():
    response = client.post(
        "/review",
        json={
            "language": "cpp",
            "code": "int main() { return 0; }",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "analyzer_unavailable"
    assert data["analyzer"]["status"] == "unavailable"
    assert data["findings"] == []


def test_empty_code_is_rejected():
    response = client.post(
        "/review",
        json={"language": "python", "code": ""},
    )

    assert response.status_code == 422


def test_unsupported_language_is_rejected():
    response = client.post(
        "/review",
        json={"language": "java", "code": "class Main {}"},
    )

    assert response.status_code == 422


def test_unexpected_fields_are_rejected():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "print('hello')",
            "admin": True,
        },
    )

    assert response.status_code == 422


def test_oversized_code_is_rejected():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "x" * 20_001,
        },
    )

    assert response.status_code == 422
