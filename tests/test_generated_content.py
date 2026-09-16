"""Contract tests for the usefulness of generated specifications."""

from __future__ import annotations


def test_product_spec_surfaces_rules_and_complete_scope(generate_bundle) -> None:
    bundle = generate_bundle()
    text = (bundle / "PRODUCT_SPEC.md").read_text(encoding="utf-8").lower()

    for topic in (
        "target user",
        "goal",
        "assumption",
        "functional requirement",
        "non-functional requirement",
        "edge case",
        "out of scope",
    ):
        assert topic in text


def test_architecture_covers_rationale_security_risks_and_extensions(generate_bundle) -> None:
    bundle = generate_bundle()
    text = (bundle / "ARCHITECTURE.md").read_text(encoding="utf-8").lower()

    for topic in ("stack", "rationale", "architecture", "security", "risk", "extension"):
        assert topic in text


def test_tasks_are_role_owned_dependency_ordered_and_testable(generate_bundle) -> None:
    bundle = generate_bundle()
    text = (bundle / "TASKS.md").read_text(encoding="utf-8").lower()

    assert "owner" in text or "role" in text
    assert "depend" in text
    assert "acceptance criteria" in text
    assert "test" in text


def test_acceptance_criteria_include_success_and_failure_states(generate_bundle) -> None:
    bundle = generate_bundle()
    text = (bundle / "ACCEPTANCE_CRITERIA.md").read_text(encoding="utf-8").lower()

    assert "given" in text and "when" in text and "then" in text
    assert "error" in text or "failure" in text


def test_agent_instructions_define_roles_and_constraints(generate_bundle) -> None:
    bundle = generate_bundle()
    text = (bundle / "AGENTS.md").read_text(encoding="utf-8").lower()

    assert "role" in text
    assert "instruction" in text or "responsibil" in text
    assert "acceptance" in text


def test_explicit_negative_constraints_are_preserved_across_documents(generate_bundle) -> None:
    idea = (
        "A developer CLI that runs entirely offline. It must never execute project code, "
        "install packages, contact registries, collect telemetry, or modify the scanned repository."
    )
    bundle = generate_bundle(idea=idea)

    product = (bundle / "PRODUCT_SPEC.md").read_text(encoding="utf-8").lower()
    architecture = (bundle / "ARCHITECTURE.md").read_text(encoding="utf-8").lower()
    agents = (bundle / "AGENTS.md").read_text(encoding="utf-8").lower()
    for text in (product, architecture, agents):
        assert "network" in text
        assert "execute" in text
        assert "install" in text
        assert "telemetry" in text
        assert "modify" in text
    assert "override generic role guidance" in agents
