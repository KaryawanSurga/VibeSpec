"""Stable Markdown renderers. Rendering deliberately avoids timestamps."""

from __future__ import annotations

from .models import ProjectIntent, Task


def _bullets(values: tuple[str, ...]) -> str:
    return "\n".join(f"- {value}" for value in values)


def product(intent: ProjectIntent) -> str:
    capabilities = tuple(f"FR-{i:02d}: {v}." for i, v in enumerate(intent.capabilities, 1))
    constraints = _bullets(intent.constraints) if intent.constraints else "- No additional explicit negative constraints were recognized; review the source idea."
    return f"""# Product specification: {intent.name}

## Source idea

{intent.idea}

## Classification and interpretation

VibeSpec classified this as a **{intent.category}** using documented keyword rules. This is a planning baseline, not a claim that ambiguous intent was inferred perfectly.

## Target users

{_bullets(intent.target_users)}

## Goals

- Let target users complete the core workflow safely and with clear feedback.
- Deliver an independently testable first release with observable success and failure states.
- Keep scope and dependencies small enough for incremental delivery.

## Functional requirements

{_bullets(capabilities)}
- FR-{len(capabilities)+1:02d}: Users receive actionable feedback for invalid input and failed operations.

## Non-functional requirements

- NFR-01 Performance: common interactions complete within 500 ms excluding third-party latency.
- NFR-02 Reliability: state-changing operations are atomic and safe to retry.
- NFR-03 Accessibility: keyboard operation and WCAG 2.2 AA contrast are release requirements.
- NFR-04 Privacy: collect only data required for the documented workflow and define retention.
- NFR-05 Portability: development and tests run from a clean checkout on supported platforms.
- NFR-06 Observability: failures include a stable error category without exposing secrets.

## Assumptions

{_bullets(intent.assumptions)}

## Edge cases and error states

- Empty, oversized, malformed, duplicated, and stale input is rejected or handled explicitly.
- Concurrent updates cannot silently overwrite newer state.
- Dependency timeouts and unavailable integrations leave recoverable state.
- First-use and empty-result screens explain the next valid action.
- Permission changes take effect before the next protected operation.

## Out of scope

- Unnamed native mobile applications, real-time collaboration, and multi-region operation.
- Custom machine-learning models or automatic interpretation of unstated requirements.
- Paid third-party integrations until separately approved.

## Explicit constraints from the idea

{constraints}
"""


def architecture(intent: ProjectIntent) -> str:
    constraints = _bullets(intent.constraints) if intent.constraints else "- No additional explicit negative constraints were recognized."
    return f"""# Architecture: {intent.name}

## Decision context

The first release needs a low-maintenance architecture for a {intent.category}. Requirements may change as assumptions are validated.

## Recommended stack

{_bullets(intent.stack)}

## Stack rationale

The modular monolith minimizes operational complexity while preserving replaceable boundaries. Python and SQLite are mature, inexpensive defaults; measurements and concrete concurrency needs must justify additional infrastructure.

## Components

1. **Delivery adapter** validates transport-specific input and maps errors to user-safe messages.
2. **Application services** coordinate use cases and transaction boundaries.
3. **Domain model** owns invariants without depending on frameworks or persistence.
4. **Repository adapters** isolate storage and external integrations behind explicit interfaces.

Dependencies point inward: adapters → application services → domain. Configuration enters at the composition root.

## Data and API contracts

- Stable identifiers are opaque strings; UTC ISO 8601 timestamps are used at boundaries.
- Inputs are schema-validated, size-limited, and normalized before domain use.
- Mutations return a result or a typed error and never expose stack traces to users.
- Schema changes use reversible, reviewed migrations with backup guidance.

## Security

- Deny access by default; authorize every protected operation server-side.
- Store secrets only in ignored environment variables or an external secret manager.
- Use parameterized persistence, output encoding, CSRF protection where applicable, and safe file paths.
- Minimize sensitive data, redact logs, rate-limit abuse-prone boundaries, and pin reviewed dependencies.

### Enforced project constraints

{constraints}

## Reliability and operations

- Make state changes atomic and idempotent where retries are possible.
- Emit structured events with correlation identifiers, never credentials or personal content.
- Define health checks, backup/restore tests, and a rollback path before production release.

## Risks and mitigations

- **Ambiguous intent:** retain assumptions in reviewable documents and revise before implementation.
- **Premature scale:** start modular and measure before adding distributed infrastructure.
- **Integration failure:** use timeouts, bounded retries, and adapter contract tests.
- **Data exposure:** threat-model trust boundaries and test authorization failures.

## Extension points

New storage, delivery channels, or optional future provider-assisted analysis belong behind adapters. Core generation and validation must remain available offline and deterministic.
"""


def tasks(intent: ProjectIntent, items: tuple[Task, ...]) -> str:
    sections = []
    for task in items:
        deps = ", ".join(task.dependencies) or "None"
        criteria = "\n".join(f"- [ ] {x}" for x in task.acceptance)
        sections.append(f"""## {task.identifier}: {task.title}

- **Owner:** {task.owner}
- **Dependencies:** {deps}
- **Goal:** {task.objective}
- **Scope boundary:** Change only artifacts needed for this task; preserve established contracts.

### Acceptance criteria

{criteria}
""")
    return f"# Delivery tasks: {intent.name}\n\nTasks are ordered by dependency and sized as independently verifiable delivery slices.\n\n" + "\n".join(sections)


def acceptance(intent: ProjectIntent, items: tuple[Task, ...]) -> str:
    rows = "\n".join(f"| {t.identifier} | {t.owner} | {'; '.join(t.acceptance)} |" for t in items)
    return f"""# Acceptance criteria: {intent.name}

## Product release gate

- Given a first-time user, when they follow the documented happy path, then the primary goal completes without undocumented setup.
- Given invalid or unauthorized input, when it is submitted, then no protected state changes and an actionable error is shown.
- Given an empty dataset or unavailable dependency, when a screen or command loads, then it presents a safe recovery action.
- Given supported desktop and narrow viewport sizes, then content remains operable without hidden controls.
- Given a clean supported environment, when the test command runs, then all automated checks pass without network access.

## Task traceability

| Task | Owner | Verifiable criteria |
| --- | --- | --- |
{rows}

## Definition of done

Code review is approved; tests and documentation are updated; security and accessibility checks pass; no secret, cache, or generated build artifact is committed; rollback is understood.
"""


def agents(intent: ProjectIntent) -> str:
    constraints = _bullets(intent.constraints) if intent.constraints else "- No additional explicit negative constraints were recognized."
    return f"""# Agent instructions: {intent.name}

These instructions are portable to common coding agents. Treat the specifications in this directory as the source of truth; ask before changing approved scope.

## Shared rules

- Work one dependency-ready task from `TASKS.md` at a time and cite its identifier.
- Read `PRODUCT_SPEC.md`, `ARCHITECTURE.md`, and relevant acceptance criteria before editing.
- Preserve user changes, never commit credentials, and do not call network services unless a task explicitly requires it.
- Validate all boundary input, keep domain rules framework-independent, and add tests for success and failure states.
- Report changed files, commands run, results, assumptions, and remaining risks. Do not claim checks you did not run.

## Non-negotiable project constraints

The following constraints were explicitly recognized in the source idea. They override generic role guidance and may not be relaxed without Product Owner approval:

{constraints}

## Roles

### Product Owner

Resolve recorded assumptions, prioritize outcomes, and accept scope. Do not prescribe implementation details unless they are product constraints.

### Tech Lead

Guard dependency direction and contracts, make small documented decisions, sequence tasks, and review security, correctness, and operational impact.

### Backend Engineer

Implement domain and application behavior behind validated interfaces. Enforce authorization and transaction boundaries; never expose secrets or raw failures.

### Frontend Engineer

Implement accessible responsive states for loading, empty, success, validation, and failure. Keep business invariants in shared/domain services.

### QA Engineer

Turn each criterion into reproducible checks. Cover boundary values, permission failures, retries, interrupted operations, supported platforms, and regression paths.

### Security Reviewer

Threat-model inputs, identity, data lifecycle, dependencies, logs, and external boundaries. Provide reproducible findings with severity and remediation.
"""
