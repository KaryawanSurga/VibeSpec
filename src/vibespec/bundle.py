"""Bundle creation and integrity validation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from .rules import analyze, build_tasks
from . import templates

DOCUMENTS = (
    "PRODUCT_SPEC.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "ACCEPTANCE_CRITERIA.md",
    "AGENTS.md",
)
MANIFEST = "vibespec.json"
REPRODUCIBILITY = "Re-run with the same VibeSpec version, normalized idea, name, and options."
CATEGORIES = {"developer tool", "booking application", "marketplace", "content application", "general application"}
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]{0,62}[a-zA-Z0-9])?$")
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


class VibeSpecError(Exception):
    """Expected user-facing error."""


def validate_name(name: str) -> str:
    if not NAME_PATTERN.fullmatch(name) or name in {".", ".."} or name.split(".", 1)[0].upper() in WINDOWS_RESERVED:
        raise VibeSpecError("invalid project name: use 1-64 letters, digits, '.', '_' or '-', starting and ending with a letter or digit")
    return name


def normalize_idea(idea: str) -> str:
    value = " ".join(idea.strip().split())
    if not value:
        raise VibeSpecError("idea must not be empty")
    if len(value) > 100_000:
        raise VibeSpecError("idea exceeds the 100,000 character limit")
    if "\x00" in value:
        raise VibeSpecError("idea contains a NUL character")
    return value


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render_bundle(name: str, idea: str) -> dict[str, bytes]:
    name = validate_name(name)
    idea = normalize_idea(idea)
    intent = analyze(name, idea)
    task_list = build_tasks(intent)
    rendered = {
        "PRODUCT_SPEC.md": templates.product(intent),
        "ARCHITECTURE.md": templates.architecture(intent),
        "TASKS.md": templates.tasks(intent, task_list),
        "ACCEPTANCE_CRITERIA.md": templates.acceptance(intent, task_list),
        "AGENTS.md": templates.agents(intent),
    }
    files = {key: (value.rstrip() + "\n").encode("utf-8") for key, value in rendered.items()}
    manifest = {
        "schema_version": 1,
        "vibespec_version": "0.1.0",
        "project": {"name": name, "category": intent.category},
        "source": {"normalized_idea_sha256": _digest(idea.encode("utf-8"))},
        "files": {filename: {"sha256": _digest(files[filename])} for filename in DOCUMENTS},
        "reproducibility": REPRODUCIBILITY,
    }
    files[MANIFEST] = (json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    return files


def generate_bundle(name: str, idea: str, output: Path | str, *, force: bool = False) -> Path:
    destination = Path(output).expanduser().resolve()
    files = render_bundle(name, idea)  # Validate everything before touching disk.
    if destination.exists() and not destination.is_dir():
        raise VibeSpecError(f"output path is not a directory: {destination}")
    conflicts = [filename for filename in files if (destination / filename).exists()]
    if conflicts and not force:
        raise VibeSpecError("refusing to overwrite existing generated files: " + ", ".join(conflicts) + "; pass --force")
    parent = destination.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.vibespec-", dir=parent))
    except OSError as exc:
        raise VibeSpecError(f"cannot prepare output path {destination}: {exc}") from exc
    backup: Path | None = None
    try:
        if destination.exists():
            shutil.copytree(destination, stage, dirs_exist_ok=True)
        for filename, content in files.items():
            (stage / filename).write_bytes(content)
        if destination.exists():
            backup = Path(tempfile.mkdtemp(prefix=f".{destination.name}.backup-", dir=parent))
            backup.rmdir()
            os.replace(destination, backup)
        os.replace(stage, destination)
        if backup is not None:
            shutil.rmtree(backup)
    except OSError as exc:
        if backup is not None and backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise VibeSpecError(f"cannot write bundle {destination}: {exc}") from exc
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
    return destination


def validate_bundle(bundle: Path | str) -> dict[str, object]:
    root = Path(bundle).expanduser().resolve()
    if not root.is_dir():
        raise VibeSpecError(f"bundle directory does not exist: {root}")
    manifest_path = root / MANIFEST
    if not manifest_path.is_file():
        raise VibeSpecError(f"missing {MANIFEST}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VibeSpecError(f"invalid {MANIFEST}: {exc}") from exc
    required_top = {"schema_version", "vibespec_version", "project", "source", "files", "reproducibility"}
    if not isinstance(manifest, dict) or set(manifest) != required_top:
        raise VibeSpecError("manifest structure is incomplete or unexpected")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1 or manifest.get("vibespec_version") != "0.1.0":
        raise VibeSpecError("unsupported or malformed manifest")
    project = manifest.get("project")
    if not isinstance(project, dict) or set(project) != {"name", "category"}:
        raise VibeSpecError("manifest project metadata is malformed")
    try:
        validate_name(project.get("name"))
    except (TypeError, VibeSpecError) as exc:
        raise VibeSpecError("manifest project name is malformed") from exc
    if not isinstance(project.get("category"), str) or project["category"] not in CATEGORIES:
        raise VibeSpecError("manifest project category is malformed")
    source = manifest.get("source")
    if not isinstance(source, dict) or set(source) != {"normalized_idea_sha256"} or not isinstance(source.get("normalized_idea_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", source["normalized_idea_sha256"]):
        raise VibeSpecError("manifest source metadata is malformed")
    if not isinstance(manifest.get("reproducibility"), str) or manifest["reproducibility"] != REPRODUCIBILITY:
        raise VibeSpecError("manifest reproducibility metadata is malformed")
    entries = manifest.get("files")
    if not isinstance(entries, dict) or set(entries) != set(DOCUMENTS):
        raise VibeSpecError("manifest file inventory is incomplete or unexpected")
    problems: list[str] = []
    for filename in DOCUMENTS:
        path = root / filename
        if not path.is_file():
            problems.append(f"missing {filename}")
            continue
        entry = entries.get(filename)
        expected = entry.get("sha256") if isinstance(entry, dict) and set(entry) == {"sha256"} else None
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            problems.append(f"invalid checksum entry for {filename}")
        elif _digest(path.read_bytes()) != expected:
            problems.append(f"checksum mismatch for {filename}")
    if problems:
        raise VibeSpecError("bundle validation failed: " + "; ".join(problems))
    return manifest
