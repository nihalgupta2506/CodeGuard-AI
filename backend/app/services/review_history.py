
import json
from typing import Any

from app.services.database import get_connection


def save_review(
    language: str,
    code: str,
    status: str,
    findings: list[dict[str, Any]],
    ai_review: dict[str, Any] | None,
) -> int:
    """Save a code review and return its database ID."""
    findings_json = json.dumps(findings)
    ai_review_json = (
        json.dumps(ai_review) if ai_review is not None else None
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO review_history (
                language,
                code,
                status,
                findings_json,
                ai_review_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                language,
                code,
                status,
                findings_json,
                ai_review_json,
            ),
        )
        return cursor.lastrowid


def list_reviews(limit: int = 20) -> list[dict[str, Any]]:
    """Return the newest reviews without their submitted source code."""
    limit = max(1, min(limit, 100))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, language, status, created_at
            FROM review_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_review(review_id: int) -> dict[str, Any] | None:
    """Retrieve a saved review by ID."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, language, code, status, findings_json,
                   ai_review_json, created_at
            FROM review_history
            WHERE id = ?
            """,
            (review_id,),
        ).fetchone()

    if row is None:
        return None

    review = dict(row)
    review["findings"] = json.loads(review.pop("findings_json"))
    ai_review_json = review.pop("ai_review_json")
    review["ai_review"] = (
        json.loads(ai_review_json) if ai_review_json else None
    )

    return review
