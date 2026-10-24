
import json
import subprocess

from app.schemas import AnalyzerInfo
from app.services import cpp_analyzer, python_analyzer


def test_python_analyzer_handles_timeout(monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd="ruff",
            timeout=10,
        )

    monkeypatch.setattr(
        python_analyzer.subprocess,
        "run",
        fake_run,
    )

    analyzer, findings = python_analyzer.analyze_python(
        "print('hello')"
    )

    assert analyzer.status == "failed"
    assert "timed out" in analyzer.message.lower()
    assert findings == []


def test_python_analyzer_handles_unavailable_tool(monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError("Ruff is unavailable")

    monkeypatch.setattr(
        python_analyzer.subprocess,
        "run",
        fake_run,
    )

    analyzer, findings = python_analyzer.analyze_python(
        "print('hello')"
    )

    assert analyzer.status == "unavailable"
    assert findings == []


def test_python_analyzer_handles_invalid_json(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "not valid json"
        stderr = ""

    monkeypatch.setattr(
        python_analyzer.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    analyzer, findings = python_analyzer.analyze_python(
        "print('hello')"
    )

    assert analyzer.status == "failed"
    assert "invalid response" in analyzer.message.lower()
    assert findings == []


def test_cpp_analyzer_handles_timeout(monkeypatch):
    monkeypatch.setattr(
        cpp_analyzer.Path,
        "is_file",
        lambda self: True,
    )

    monkeypatch.setattr(
        cpp_analyzer.subprocess,
        "run",
        lambda *args, **kwargs: (
            _raise_timeout()
        ),
    )

    analyzer, findings = cpp_analyzer.analyze_cpp(
        "int main() { return 0; }"
    )

    assert analyzer.status == "failed"
    assert "timed out" in analyzer.message.lower()
    assert findings == []



def _raise_timeout(*args, **kwargs):
    raise subprocess.TimeoutExpired(
        cmd=kwargs.get("args", args[0] if args else "analyzer"),
        timeout=kwargs.get("timeout", 15),
    )



def test_cpp_analyzer_handles_unavailable_tool(monkeypatch):
    monkeypatch.setattr(
        cpp_analyzer.Path,
        "is_file",
        lambda self: False,
    )
    monkeypatch.setattr(
        cpp_analyzer.shutil,
        "which",
        lambda name: None,
    )

    analyzer, findings = cpp_analyzer.analyze_cpp(
        "int main() { return 0; }"
    )

    assert analyzer.status == "unavailable"
    assert findings == []

from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("module", "analyze", "source_code"),
    [
        (
            python_analyzer,
            python_analyzer.analyze_python,
            "print('hello')",
        ),
        (
            cpp_analyzer,
            cpp_analyzer.analyze_cpp,
            "int main() { return 0; }",
        ),
    ],
)
def test_temporary_source_file_is_removed_after_timeout(
    monkeypatch,
    tmp_path,
    module,
    analyze,
    source_code,
):
    created_paths = []
    original_named_temporary_file = module.tempfile.NamedTemporaryFile

    def tracked_temporary_file(*args, **kwargs):
        temporary_file = original_named_temporary_file(
            *args,
            dir=tmp_path,
            **kwargs,
        )
        created_paths.append(Path(temporary_file.name))
        return temporary_file

    monkeypatch.setattr(
        module.tempfile,
        "NamedTemporaryFile",
        tracked_temporary_file,
    )

    if module is cpp_analyzer:
        monkeypatch.setattr(
            cpp_analyzer.Path,
            "is_file",
            lambda self: True,
        )

    monkeypatch.setattr(
        module.subprocess,
        "run",
        _raise_timeout,
    )

    analyzer, findings = analyze(source_code)

    assert analyzer.status == "failed"
    assert findings == []
    assert len(created_paths) == 1
    assert not created_paths[0].exists()

def test_cpp_analyzer_handles_nonzero_exit_without_diagnostics(
    monkeypatch,
):
    monkeypatch.setattr(
        cpp_analyzer.Path,
        "is_file",
        lambda self: True,
    )

    class FakeResult:
        returncode = 1
        stdout = ""
        stderr = "clang-tidy failed"

    monkeypatch.setattr(
        cpp_analyzer.subprocess,
        "run",
        lambda *args, **kwargs: FakeResult(),
    )

    analyzer, findings = cpp_analyzer.analyze_cpp(
        "int main() { return 0; }"
    )

    assert analyzer.status == "failed"
    assert findings == []


def test_cpp_analyzer_handles_os_error(monkeypatch):
    monkeypatch.setattr(
        cpp_analyzer.Path,
        "is_file",
        lambda self: True,
    )

    def fake_run(*args, **kwargs):
        raise OSError("Simulated operating-system error")

    monkeypatch.setattr(
        cpp_analyzer.subprocess,
        "run",
        fake_run,
    )

    analyzer, findings = cpp_analyzer.analyze_cpp(
        "int main() { return 0; }"
    )

    assert analyzer.status == "unavailable"
    assert findings == []
