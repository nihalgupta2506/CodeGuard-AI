
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



def test_cpp_analyzer_returns_structured_response():
    response = client.post(
        "/review",
        json={
            "language": "cpp",
            "code": "int main() { return 0; }",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["language"] == "cpp"
    assert data["status"] == "completed"
    assert data["analyzer"]["name"] == "clang-tidy"
    assert data["analyzer"]["status"] == "completed"
    assert isinstance(data["findings"], list)
    assert data["findings_count"] == len(data["findings"])


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

def test_whitespace_only_code_is_rejected():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "   \n\t   ",
        },
    )

    assert response.status_code == 422


def test_code_at_maximum_length_is_accepted_by_validation():
    from app.schemas import ReviewRequest

    payload = ReviewRequest(
        language="python",
        code=" " + ("x" * 19_999),
    )

    assert len(payload.code) == 20_000


def test_invalid_language_case_is_rejected():
    response = client.post(
        "/review",
        json={
            "language": "Python",
            "code": "print('hello')",
        },
    )

    assert response.status_code == 422


def test_null_code_is_rejected():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": None,
        },
    )

    assert response.status_code == 422

def test_request_with_oversized_content_length_is_rejected():
    response = client.post(
        "/review",
        content=b'{"language":"python","code":"print(1)"}',
        headers={"Content-Length": "25001"},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body is too large."


def test_request_with_invalid_content_length_is_rejected():
    response = client.post(
        "/review",
        content=b'{"language":"python","code":"print(1)"}',
        headers={"Content-Length": "invalid"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Content-Length header."


def test_request_with_small_content_length_is_not_rejected_by_size_middleware():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ai_failure_preserves_static_findings(monkeypatch):
    from app import main

    def fake_ai_review(**kwargs):
        raise RuntimeError("Sensitive internal error")

    monkeypatch.setattr(
        main,
        "explain_code_findings",
        fake_ai_review,
    )

    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "import os\nprint('hello')\n",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert any(
        finding["rule_id"] == "F401"
        for finding in data["findings"]
    )
    assert data["ai_review"]["status"] == "failed"
    assert "Sensitive internal error" not in response.text


def test_malformed_ai_result_preserves_static_findings(
    monkeypatch,
):
    from app import main

    def fake_ai_review(**kwargs):
        return {"unexpected": "response"}

    monkeypatch.setattr(
        main,
        "explain_code_findings",
        fake_ai_review,
    )

    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "import os\nprint('hello')\n",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["findings_count"] == len(data["findings"])
    assert any(
        finding["rule_id"] == "F401"
        for finding in data["findings"]
    )
    assert data["ai_review"]["status"] == "failed"

def test_database_save_failure_does_not_break_review(monkeypatch):
    from app import main

    def fake_save_review(**kwargs):
        raise RuntimeError("Sensitive database error")

    monkeypatch.setattr(
        main,
        "save_review",
        fake_save_review,
    )

    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "import os\nprint('hello')\n",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["findings_count"] == len(data["findings"])
    assert "Sensitive database error" not in response.text

def test_review_history_list_does_not_expose_source_code():
    response = client.get("/reviews")

    assert response.status_code == 200

    data = response.json()

    assert "reviews" in data

    for review in data["reviews"]:
        assert "code" not in review
