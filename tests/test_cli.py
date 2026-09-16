"""End-to-end tests for the public command-line contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


CONTRACTED_DOCUMENTS = {
    "PRODUCT_SPEC.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "ACCEPTANCE_CRITERIA.md",
    "AGENTS.md",
    "vibespec.json",
}


def snapshot(directory: Path) -> dict[str, str]:
    """Return content hashes without relying on filesystem timestamps."""
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def test_module_help_lists_supported_workflow(run_cli) -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    for command in ("init", "generate", "validate", "export-agents"):
        assert command in result.stdout


def test_init_writes_utf8_sample_that_can_be_generated(run_cli, tmp_path: Path) -> None:
    sample = tmp_path / "sample.md"

    initialized = run_cli("init", sample)

    assert initialized.returncode == 0, initialized.stderr
    assert sample.is_file()
    assert sample.read_text(encoding="utf-8").strip()
    output = tmp_path / "from-sample"
    generated = run_cli(
        "generate", "--input", sample, "--name", "from-sample", "--output", output
    )
    assert generated.returncode == 0, generated.stderr
    assert CONTRACTED_DOCUMENTS <= {path.name for path in output.iterdir()}


def test_init_does_not_replace_existing_sample_without_overwrite(run_cli, tmp_path: Path) -> None:
    sample = tmp_path / "idea.md"
    sample.write_text("keep me", encoding="utf-8")

    result = run_cli("init", sample)

    assert result.returncode != 0
    assert sample.read_text(encoding="utf-8") == "keep me"


def test_init_force_explicitly_replaces_existing_sample(run_cli, tmp_path: Path) -> None:
    sample = tmp_path / "idea.md"
    sample.write_text("old contents", encoding="utf-8")

    result = run_cli("init", sample, "--force")

    assert result.returncode == 0, result.stderr
    assert sample.read_text(encoding="utf-8") != "old contents"


def test_generate_creates_complete_valid_bundle(run_cli, idea_file: Path, tmp_path: Path) -> None:
    output = tmp_path / "neighborhood-booking"

    generated = run_cli(
        "generate",
        "--input",
        idea_file,
        "--name",
        "neighborhood-booking",
        "--output",
        output,
    )

    assert generated.returncode == 0, generated.stderr
    assert CONTRACTED_DOCUMENTS <= {path.name for path in output.iterdir()}
    manifest = json.loads((output / "vibespec.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["vibespec_version"] == "0.1.0"
    assert manifest["project"]["name"] == "neighborhood-booking"
    assert manifest.get("files")
    validated = run_cli("validate", output)
    assert validated.returncode == 0, validated.stderr


def test_generation_is_byte_for_byte_deterministic(run_cli, tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    common = ("--idea", "A CLI that checks repository health", "--name", "repo-health")

    one = run_cli("generate", *common, "--output", first)
    two = run_cli("generate", *common, "--output", second)

    assert one.returncode == two.returncode == 0
    assert snapshot(first) == snapshot(second)


def test_utf8_idea_is_preserved_in_generated_spec(run_cli, tmp_path: Path) -> None:
    output = tmp_path / "agenda-komunitas"
    idea = "Aplikasi jadwal komunitas untuk warga Jakarta — cepat, aman, dan ramah."

    result = run_cli(
        "generate", "--idea", idea, "--name", "agenda-komunitas", "--output", output
    )

    assert result.returncode == 0, result.stderr
    assert idea in (output / "PRODUCT_SPEC.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("idea", ["", " ", "\n\t"])
def test_empty_idea_fails_without_creating_output(run_cli, tmp_path: Path, idea: str) -> None:
    output = tmp_path / "empty"

    result = run_cli("generate", "--idea", idea, "--name", "empty", "--output", output)

    assert result.returncode != 0
    assert not output.exists()
    assert "empty" in result.stderr.lower() or "idea" in result.stderr.lower()


@pytest.mark.parametrize(
    "name",
    ["../escape", "nested/project", r"nested\\project", ".", "..", "CON", "bad:name"],
)
def test_unsafe_project_names_fail_without_output(run_cli, tmp_path: Path, name: str) -> None:
    output = tmp_path / "unsafe"

    result = run_cli("generate", "--idea", "A useful app", "--name", name, "--output", output)

    assert result.returncode != 0
    assert not output.exists()


def test_missing_input_file_fails_without_output(run_cli, tmp_path: Path) -> None:
    output = tmp_path / "missing-input"
    result = run_cli(
        "generate",
        "--input",
        tmp_path / "does-not-exist.md",
        "--name",
        "missing-input",
        "--output",
        output,
    )
    assert result.returncode != 0
    assert not output.exists()


def test_empty_input_file_fails_without_output(run_cli, tmp_path: Path) -> None:
    source = tmp_path / "empty.md"
    source.write_text("\n\t", encoding="utf-8")
    output = tmp_path / "empty-input"

    result = run_cli(
        "generate", "--input", source, "--name", "empty-input", "--output", output
    )

    assert result.returncode != 0
    assert not output.exists()
    assert "empty" in (result.stderr + result.stdout).lower()


def test_generate_rejects_ambiguous_idea_sources(run_cli, idea_file: Path, tmp_path: Path) -> None:
    output = tmp_path / "ambiguous"

    result = run_cli(
        "generate",
        "--idea",
        "Inline idea",
        "--input",
        idea_file,
        "--name",
        "ambiguous",
        "--output",
        output,
    )

    assert result.returncode != 0
    assert not output.exists()


def test_existing_bundle_is_untouched_without_overwrite(run_cli, tmp_path: Path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    sentinel = output / "PRODUCT_SPEC.md"
    sentinel.write_bytes(b"irreplaceable\r\ncontent")
    before = snapshot(output)

    result = run_cli(
        "generate", "--idea", "A changed idea", "--name", "existing", "--output", output
    )

    assert result.returncode != 0
    assert snapshot(output) == before
    assert sentinel.read_bytes() == b"irreplaceable\r\ncontent"


def test_overwrite_requires_flag_and_replaces_generated_files(run_cli, tmp_path: Path) -> None:
    output = tmp_path / "overwrite"
    first = run_cli(
        "generate", "--idea", "First idea", "--name", "overwrite", "--output", output
    )
    assert first.returncode == 0
    old = snapshot(output)

    second = run_cli(
        "generate",
        "--idea",
        "Second idea",
        "--name",
        "overwrite",
        "--output",
        output,
        "--force",
    )

    assert second.returncode == 0, second.stderr
    assert snapshot(output) != old
    assert "Second idea" in (output / "PRODUCT_SPEC.md").read_text(encoding="utf-8")


def test_validate_rejects_missing_document(run_cli, generate_bundle) -> None:
    output = generate_bundle()
    (output / "TASKS.md").unlink()

    result = run_cli("validate", output)

    assert result.returncode != 0
    assert "TASKS.md" in result.stderr + result.stdout


def test_validate_rejects_tampered_document(run_cli, generate_bundle) -> None:
    output = generate_bundle()
    with (output / "ARCHITECTURE.md").open("a", encoding="utf-8") as stream:
        stream.write("\nTampered after generation.\n")

    result = run_cli("validate", output)

    assert result.returncode != 0
    assert "ARCHITECTURE.md" in result.stderr + result.stdout


def test_validate_rejects_malformed_manifest(run_cli, generate_bundle) -> None:
    output = generate_bundle()
    (output / "vibespec.json").write_text("{not json", encoding="utf-8")

    result = run_cli("validate", output)

    assert result.returncode != 0
    assert "vibespec.json" in (result.stderr + result.stdout).lower()


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda data: data.pop("project"), "structure"),
        (lambda data: data["project"].update(name=[]), "project name"),
        (lambda data: data["project"].update(category="invented"), "category"),
        (lambda data: data["source"].update(normalized_idea_sha256="not-a-hash"), "source"),
        (lambda data: data.update(reproducibility=False), "reproducibility"),
        (lambda data: data.update(unexpected="field"), "structure"),
        (lambda data: data["files"]["AGENTS.md"].update(extra=True), "AGENTS.md"),
    ],
)
def test_validate_rejects_missing_or_tampered_manifest_metadata(
    run_cli, generate_bundle, mutation, expected: str
) -> None:
    import json

    output = generate_bundle()
    path = output / "vibespec.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    mutation(data)
    path.write_text(json.dumps(data), encoding="utf-8")

    result = run_cli("validate", output)

    assert result.returncode != 0
    assert expected.lower() in (result.stderr + result.stdout).lower()


def test_failed_validation_never_modifies_bundle(run_cli, generate_bundle) -> None:
    output = generate_bundle()
    (output / "AGENTS.md").unlink()
    before = snapshot(output)

    result = run_cli("validate", output)

    assert result.returncode != 0
    assert snapshot(output) == before


def test_export_agents_writes_requested_file(run_cli, generate_bundle, tmp_path: Path) -> None:
    bundle = generate_bundle()
    exported = tmp_path / "agent-instructions.md"

    result = run_cli("export-agents", bundle, "--output", exported)

    assert result.returncode == 0, result.stderr
    assert exported.is_file()
    text = exported.read_text(encoding="utf-8")
    assert text.strip()
    assert "agent" in text.lower()


def test_export_agents_protects_existing_destination(run_cli, generate_bundle, tmp_path: Path) -> None:
    bundle = generate_bundle()
    exported = tmp_path / "agent-instructions.md"
    exported.write_text("do not replace", encoding="utf-8")

    result = run_cli("export-agents", bundle, "--output", exported)

    assert result.returncode != 0
    assert exported.read_text(encoding="utf-8") == "do not replace"


def test_export_agents_force_explicitly_replaces_destination(
    run_cli, generate_bundle, tmp_path: Path
) -> None:
    bundle = generate_bundle()
    exported = tmp_path / "agent-instructions.md"
    exported.write_text("old contents", encoding="utf-8")

    result = run_cli("export-agents", bundle, "--output", exported, "--force")

    assert result.returncode == 0, result.stderr
    assert exported.read_text(encoding="utf-8") != "old contents"
