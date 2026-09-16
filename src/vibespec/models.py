"""Typed domain models used by the deterministic rule engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProjectIntent:
    name: str
    idea: str
    category: str
    target_users: tuple[str, ...]
    capabilities: tuple[str, ...]
    assumptions: tuple[str, ...]
    stack: tuple[str, ...]
    constraints: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Task:
    identifier: str
    title: str
    owner: str
    dependencies: tuple[str, ...]
    objective: str
    acceptance: tuple[str, ...]
