"""Transparent keyword rules. Order is significant and stable."""

from __future__ import annotations

import re

from .models import ProjectIntent, Task

CATEGORY_RULES = (
    ("developer tool", ("cli", "developer", "api", "sdk", "terminal", "repository")),
    ("booking application", ("booking", "appointment", "reservation", "schedule")),
    ("marketplace", ("marketplace", "seller", "buyer", "catalog")),
    ("content application", ("blog", "content", "article", "newsletter")),
)

CAPABILITY_RULES = (
    ("Account and access management", ("user", "account", "login", "team", "admin")),
    ("Search and filtering", ("search", "filter", "find", "catalog")),
    ("Scheduling and availability", ("book", "schedule", "appointment", "calendar", "reservation")),
    ("Notifications", ("notify", "notification", "email", "reminder")),
    ("Payments and billing", ("payment", "billing", "checkout", "subscription")),
    ("Import and export", ("import", "export", "file", "markdown", "csv")),
    ("Command-line workflow", ("cli", "terminal", "command")),
)

# Negative requirements are preserved as constraints rather than inferred as
# capabilities. Phrase order is stable and intentionally narrow.
CONSTRAINT_RULES = (
    ("Do not use network access or contact remote services.", (r"\b(?:no|without) network\b", r"\boffline\b", r"\bnever contact\b", r"\bnot contact\b")),
    ("Do not call external APIs.", (r"\bno (?:external )?api(?:s)?\b", r"\bwithout (?:external )?api(?:s)?\b")),
    ("Do not collect or transmit telemetry.", (r"\bno telemetry\b", r"\bnever collect telemetry\b", r"\bnot collect telemetry\b", r"\b(?:never|do not|must not)[^.]{0,200}\bcollect telemetry\b")),
    ("Do not execute project or user-supplied code.", (r"\bnever execute\b", r"\bdo not execute\b", r"\bmust not execute\b")),
    ("Do not install packages or dependencies.", (r"\bnever install\b", r"\bdo not install\b", r"\bmust not install\b", r"\b(?:never|do not|must not)[^.]{0,200}\binstall (?:packages|dependencies)\b")),
    ("Do not modify the inspected repository or project.", (r"\bnever modify\b", r"\bdo not modify\b", r"\bmust not modify\b", r"\b(?:never|do not|must not)[^.]{0,200}\bmodify (?:the )?(?:scanned )?(?:repository|project)\b")),
)


def _contains(text: str, words: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\w*\b", text, re.IGNORECASE) for word in words)


def analyze(name: str, idea: str) -> ProjectIntent:
    normalized = " ".join(idea.split())
    category = "general application"
    for candidate, words in CATEGORY_RULES:
        if _contains(normalized, words):
            category = candidate
            break
    capabilities = tuple(label for label, words in CAPABILITY_RULES if _contains(normalized, words))
    if not capabilities:
        capabilities = ("Core workflow described by the idea",)
    target_users = {
        "developer tool": ("Software developers", "Engineering teams"),
        "booking application": ("People making bookings", "Service operators"),
        "marketplace": ("Buyers", "Sellers", "Marketplace operators"),
        "content application": ("Readers", "Content publishers"),
    }.get(category, ("End users of the proposed application", "Project maintainers"))
    stack = (
        "Python 3.11+ for a portable, mature implementation",
        "SQLite for local persistence; migrate only when concurrent writes require it",
        "A server-rendered web UI when a graphical interface is required",
        "pytest for fast deterministic verification",
    )
    assumptions = (
        "The idea text is the sole source of product intent; ambiguous details use documented defaults.",
        "The first release serves a single region and English-language interface.",
        "Accessibility, privacy, and secure defaults are required even when not named explicitly.",
        "External integrations are adapters and may be replaced without changing core domain logic.",
    )
    lowered = normalized.lower()
    constraints = tuple(label for label, patterns in CONSTRAINT_RULES if any(re.search(pattern, lowered) for pattern in patterns))
    return ProjectIntent(name, normalized, category, target_users, capabilities, assumptions, stack, constraints)


def build_tasks(intent: ProjectIntent) -> tuple[Task, ...]:
    feature_tasks = tuple(
        Task(
            f"TASK-{index:03d}",
            f"Implement {capability.lower()}",
            "Backend Engineer" if index % 2 else "Frontend Engineer",
            ("TASK-002",),
            f"Deliver the smallest end-to-end slice for {capability.lower()}.",
            (
                "Given valid input, the workflow completes and persists or displays the expected result.",
                "Invalid, empty, and unauthorized input produces a clear error without partial state.",
                "Automated tests cover the success path and at least one failure path.",
            ),
        )
        for index, capability in enumerate(intent.capabilities, 3)
    )
    last_features = tuple(task.identifier for task in feature_tasks) or ("TASK-002",)
    return (
        Task("TASK-001", "Confirm product contract", "Product Owner", (), "Resolve assumptions and approve explicit scope.",
             ("Target users and measurable goals are approved.", "Out-of-scope items and unresolved assumptions are recorded.")),
        Task("TASK-002", "Establish architecture and quality baseline", "Tech Lead", ("TASK-001",),
             "Create the project skeleton, domain boundaries, CI, and test harness.",
             ("The application starts from a clean checkout.", "CI runs formatting, security-safe checks, and tests.", "No credentials or environment-specific paths are committed.")),
        *feature_tasks,
        Task(f"TASK-{len(feature_tasks)+3:03d}", "Verify release candidate", "QA Engineer", last_features,
             "Validate the integrated product against this specification.",
             ("All acceptance criteria pass on supported platforms.", "Accessibility and security checks have no unresolved high-severity findings.", "Rollback and recovery behavior is documented.")),
    )
