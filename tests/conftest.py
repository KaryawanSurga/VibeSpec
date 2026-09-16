"""Shared black-box helpers for the VibeSpec CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def run_cli(tmp_path: Path):
    """Run the source checkout's CLI in an isolated working directory."""

    def run(*args: object, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        src = Path(__file__).resolve().parents[1] / "src"
        current = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(src) if not current else os.pathsep.join((str(src), current))
        result = subprocess.run(
            [sys.executable, "-m", "vibespec", *(str(arg) for arg in args)],
            cwd=cwd or tmp_path,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        assert "Traceback (most recent call last)" not in result.stderr, (
            "CLI leaked an internal traceback instead of a useful error:\n" + result.stderr
        )
        return result

    return run


@pytest.fixture
def idea_file(tmp_path: Path) -> Path:
    path = tmp_path / "idea.md"
    path.write_text(
        "# Neighborhood booking\n\n"
        "A mobile-friendly booking app for neighbors to reserve shared rooms. "
        "Admins can approve bookings and users receive clear conflict errors.\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def generate_bundle(run_cli, tmp_path: Path):
    def generate(*extra: object, idea: str = "A booking app for shared studios") -> Path:
        output = tmp_path / "booking-app"
        result = run_cli(
            "generate",
            "--idea",
            idea,
            "--name",
            "booking-app",
            "--output",
            output,
            *extra,
        )
        assert result.returncode == 0, result.stderr or result.stdout
        return output

    return generate
