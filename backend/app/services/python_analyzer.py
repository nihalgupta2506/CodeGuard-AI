
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from app.schemas import AnalyzerInfo, Finding


def analyze_python(code: str) -> tuple[AnalyzerInfo, list[Finding]]:
    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".py",
            prefix="codeguard_",
            delete=False,
            newline="",
        ) as source_file:
            source_file.write(code)
            temp_path = source_file.name

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--output-format=json",
                "--no-fix",
                temp_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
            shell=False,
        )

        if result.returncode not in (0, 1):
            return (
                AnalyzerInfo(
                    name="Ruff",
                    status="failed",
                    message="Ruff could not complete the analysis.",
                ),
                [],
            )

        try:
            raw_findings = json.loads(result.stdout)
        except json.JSONDecodeError:
            return (
                AnalyzerInfo(
                    name="Ruff",
                    status="failed",
                    message="Ruff returned an invalid response.",
                ),
                [],
            )

        if not isinstance(raw_findings, list):
            return (
                AnalyzerInfo(
                    name="Ruff",
                    status="failed",
                    message="Ruff returned an unexpected response format.",
                ),
                [],
            )

        findings: list[Finding] = []

        for item in raw_findings:
            if not isinstance(item, dict):
                continue

            code_id = item.get("code")
            message = item.get("message")
            location = item.get("location")

            if (
                not isinstance(code_id, str)
                or not isinstance(message, str)
                or not isinstance(location, dict)
                or not isinstance(location.get("row"), int)
                or not isinstance(location.get("column"), int)
            ):
                continue

            severity = (
                "error"
                if code_id.startswith(("E", "F"))
                else "warning"
            )

            end_location = item.get("end_location")
            if not isinstance(end_location, dict):
                end_location = {}

            fix = item.get("fix")

            findings.append(
                Finding(
                    source="static_analysis",
                    rule_id=code_id,
                    severity=severity,
                    message=message,
                    line=location["row"],
                    column=location["column"],
                    end_line=end_location.get("row"),
                    end_column=end_location.get("column"),
                    fix_available=isinstance(fix, dict),
                )
            )

        return (
            AnalyzerInfo(
                name="Ruff",
                status="completed",
                message="Static analysis completed successfully.",
            ),
            findings,
        )

    except subprocess.TimeoutExpired:
        return (
            AnalyzerInfo(
                name="Ruff",
                status="failed",
                message="Analysis timed out.",
            ),
            [],
        )

    except OSError:
        return (
            AnalyzerInfo(
                name="Ruff",
                status="unavailable",
                message="Ruff could not be started in this environment.",
            ),
            [],
        )

    finally:
        if temp_path is not None:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass
