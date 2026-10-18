
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: Literal["python", "cpp"]
    code: str = Field(min_length=1, max_length=20_000)

    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Source code must not be blank.")
        return value


class Finding(BaseModel):
    source: Literal["static_analysis"]
    rule_id: str
    severity: Literal["error", "warning", "info"]
    message: str
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None
    fix_available: bool = False


class AnalyzerInfo(BaseModel):
    name: str
    status: Literal["completed", "unavailable", "failed"]
    message: str


class ReviewResponse(BaseModel):
    language: Literal["python", "cpp"]
    status: Literal["completed", "analyzer_unavailable", "failed"]
    analyzer: AnalyzerInfo
    findings: list[Finding]
    findings_count: int
