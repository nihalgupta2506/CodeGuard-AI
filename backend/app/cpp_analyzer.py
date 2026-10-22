
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.schemas import AnalyzerInfo, Finding


LLVM_BIN = Path(r"C:\Program Files\LLVM\bin")
CLANG_TIDY = shutil.which("clang-tidy") or str(
    LLVM_BIN / "clang-tidy.exe"
)

ENABLED_CHECKS = (
    "-*,bugprone-*,cert-*,clang-analyzer-*,"
    "performance-*,portability-*,readability-*"
)

DIAGNOSTIC_PATTERN = re.compile(
    r":(?P<line>\d+):(?P<column>\d+): "
    r"(?P<severity>warning|error): "
    r"(?P<message>.*?)"
    r"(?: \[(?P<rule>[^\]]+)\])?$"
)


def analyze_cpp(code: str) -> tuple[AnalyzerInfo, list[Finding]]:
    """Analyze C++ source without executing the submitted program."""
    if not Path(CLANG_TIDY).is_file() and not shutil.which(CLANG_TIDY):
        return (
            AnalyzerInfo(
                name="clang-tidy",
                status="unavailable",
                message="clang-tidy is not installed or cannot be located.",
            ),
            [],
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".cpp",
            prefix="codeguard_",
            delete=False,
            newline="",
        ) as source_file:
            source_file.write(code)
            temp_path = source_file.name

        result = subprocess.run(
            [
                CLANG_TIDY,
                "--quiet",
                f"--checks={ENABLED_CHECKS}",
                temp_path,
                "--",
                "-std=c++17",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
            shell=False,
        )

        output = "\n".join(
            part for part in (result.stdout, result.stderr) if part
        )
        findings = []

        for line in output.splitlines():
            match = DIAGNOSTIC_PATTERN.search(line)
            if not match:
                continue

            severity = match.group("severity")
            rule = match.group("rule") or (
                "clang-diagnostic-error"
                if severity == "error"
                else "clang-diagnostic-warning"
            )

            findings.append(
                Finding(
                    source="static_analysis",
                    rule_id=rule,
                    severity=severity,
                    message=match.group("message"),
                    line=int(match.group("line")),
                    column=int(match.group("column")),
                    fix_available=False,
                )
            )

        if result.returncode != 0 and not findings:
            return (
                AnalyzerInfo(
                    name="clang-tidy",
                    status="failed",
                    message="C++ analysis could not complete.",
                ),
                [],
            )

        return (
            AnalyzerInfo(
                name="clang-tidy",
                status="completed",
                message="C++ static analysis completed successfully.",
            ),
            findings,
        )

    except subprocess.TimeoutExpired:
        return (
            AnalyzerInfo(
                name="clang-tidy",
                status="failed",
                message="C++ analysis timed out.",
            ),
            [],
        )
    except OSError:
        return (
            AnalyzerInfo(
                name="clang-tidy",
                status="unavailable",
                message="clang-tidy could not be started.",
            ),
            [],
        )
    finally:
        if temp_path is not None:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass
