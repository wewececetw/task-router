"""Spec Kit phase-aware routing.

Maps Spec Kit workflow phases to routing decisions:
- constitution, specify, plan, clarify → cloud (Claude) — requires deep reasoning
- tasks, checklist, analyze → local (oMLX) — structured transformation
- implement → depends on individual task complexity
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class SpecPhase(str, Enum):
    """Spec Kit development phases."""
    CONSTITUTION = "constitution"
    SPECIFY = "specify"
    CLARIFY = "clarify"
    PLAN = "plan"
    TASKS = "tasks"
    IMPLEMENT = "implement"
    ANALYZE = "analyze"
    CHECKLIST = "checklist"
    UNKNOWN = "unknown"


@dataclass
class PhaseRouting:
    """Routing decision for a Spec Kit phase."""
    phase: SpecPhase
    backend: str  # "local" or "cloud"
    reason: str
    allow_override: bool  # Can task-level complexity override?


# Static routing table: phase → default backend
PHASE_ROUTING: dict[SpecPhase, PhaseRouting] = {
    SpecPhase.CONSTITUTION: PhaseRouting(
        phase=SpecPhase.CONSTITUTION,
        backend="cloud",
        reason="Constitution defines project-wide principles — needs deep reasoning",
        allow_override=False,
    ),
    SpecPhase.SPECIFY: PhaseRouting(
        phase=SpecPhase.SPECIFY,
        backend="cloud",
        reason="Specification requires understanding requirements and user stories",
        allow_override=False,
    ),
    SpecPhase.CLARIFY: PhaseRouting(
        phase=SpecPhase.CLARIFY,
        backend="cloud",
        reason="Clarification needs contextual understanding to find gaps",
        allow_override=False,
    ),
    SpecPhase.PLAN: PhaseRouting(
        phase=SpecPhase.PLAN,
        backend="cloud",
        reason="Architecture and design decisions need strong reasoning",
        allow_override=False,
    ),
    SpecPhase.TASKS: PhaseRouting(
        phase=SpecPhase.TASKS,
        backend="local",
        reason="Task breakdown is structured transformation from plan",
        allow_override=False,
    ),
    SpecPhase.IMPLEMENT: PhaseRouting(
        phase=SpecPhase.IMPLEMENT,
        backend="local",  # default, but can be overridden by task complexity
        reason="Implementation routes by individual task complexity",
        allow_override=True,
    ),
    SpecPhase.ANALYZE: PhaseRouting(
        phase=SpecPhase.ANALYZE,
        backend="local",
        reason="Consistency checking is pattern-matching work",
        allow_override=False,
    ),
    SpecPhase.CHECKLIST: PhaseRouting(
        phase=SpecPhase.CHECKLIST,
        backend="local",
        reason="Checklist generation is structured output",
        allow_override=False,
    ),
}


# Patterns to detect which Spec Kit phase a task belongs to.
# Order matters: more specific patterns first (e.g. "speckit.tasks" before generic "plan").
PHASE_DETECTORS: list[tuple[SpecPhase, re.Pattern]] = [
    (SpecPhase.CONSTITUTION, re.compile(r"(?:speckit\.)?constitution|核心原則|core.?principles", re.I)),
    (SpecPhase.CHECKLIST, re.compile(r"(?:speckit\.)?checklist|檢查清單|quality.?check", re.I)),
    (SpecPhase.TASKS, re.compile(r"(?:speckit\.)?tasks?\b|task.?list|任務列表|task.?breakdown", re.I)),
    (SpecPhase.ANALYZE, re.compile(r"(?:speckit\.)?analy[zs]e|一致性|consistency.?check", re.I)),
    (SpecPhase.IMPLEMENT, re.compile(r"(?:speckit\.)?implement|執行|實作|write.?code|coding", re.I)),
    (SpecPhase.CLARIFY, re.compile(r"(?:speckit\.)?clarify|釐清|澄清|underspecified", re.I)),
    (SpecPhase.SPECIFY, re.compile(r"(?:speckit\.)?spec(?:ify)?(?:\s|$)|需求|requirement|user.?stor", re.I)),
    (SpecPhase.PLAN, re.compile(r"(?:speckit\.)?plan\b|implementation.?plan|架構|architecture.?design", re.I)),
]

# Implementation tasks that are simple enough for local model
SIMPLE_IMPL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("create_model", re.compile(r"create.*model|create.*schema|create.*entity", re.I)),
    ("create_config", re.compile(r"create.*config|setup.*config|configure", re.I)),
    ("boilerplate", re.compile(r"boilerplate|scaffold|template|project.?structure", re.I)),
    ("crud", re.compile(r"CRUD|create.*endpoint|basic.*api|simple.*route", re.I)),
    ("add_dependency", re.compile(r"add.*dependency|install.*package|setup.*tool", re.I)),
    ("formatting", re.compile(r"lint|format|prettier|style", re.I)),
    ("documentation", re.compile(r"document|README|docstring|comment", re.I)),
    ("test_simple", re.compile(r"unit.?test|simple.?test|test.*model", re.I)),
    ("migration", re.compile(r"migration|schema.*change|add.*column", re.I)),
    ("env_setup", re.compile(r"environment|\.env|docker.?compose|setup", re.I)),
]

# Implementation tasks that need cloud model
COMPLEX_IMPL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("auth", re.compile(r"auth(?:entication|orization)|OAuth|JWT|session|login", re.I)),
    ("security", re.compile(r"security|encrypt|hash|vulnerab|CSRF|XSS", re.I)),
    ("core_logic", re.compile(r"core.?logic|business.?logic|algorithm|state.?machine", re.I)),
    ("integration", re.compile(r"integrat(?:e|ion)|third.?party|external.?api|webhook", re.I)),
    ("error_handling", re.compile(r"error.?handling|retry|circuit.?break|fault.?toleran", re.I)),
    ("performance", re.compile(r"optimi[zs]|cach(?:e|ing)|performance|concurrent", re.I)),
    ("data_pipeline", re.compile(r"pipeline|ETL|data.?flow|stream|queue", re.I)),
    ("complex_query", re.compile(r"complex.?query|aggregat|join.*table|analytics", re.I)),
]


def detect_phase(task: str) -> SpecPhase:
    """Detect which Spec Kit phase a task belongs to."""
    for phase, pattern in PHASE_DETECTORS:
        if pattern.search(task):
            return phase
    return SpecPhase.UNKNOWN


def classify_impl_task(task_description: str) -> str:
    """For implementation phase, decide if a specific task is simple or complex.

    Returns "local" or "cloud".
    """
    simple_score = sum(1 for _, p in SIMPLE_IMPL_PATTERNS if p.search(task_description))
    complex_score = sum(1.5 for _, p in COMPLEX_IMPL_PATTERNS if p.search(task_description))

    if complex_score > simple_score:
        return "cloud"
    return "local"


def route_phase(task: str, phase: SpecPhase | None = None) -> PhaseRouting:
    """Determine routing for a task based on its Spec Kit phase.

    Args:
        task: The task description or prompt
        phase: Explicit phase override. If None, auto-detect from task text.

    Returns:
        PhaseRouting with backend decision
    """
    if phase is None:
        phase = detect_phase(task)

    if phase == SpecPhase.UNKNOWN:
        # Fall back to generic classification
        return PhaseRouting(
            phase=SpecPhase.UNKNOWN,
            backend="cloud",
            reason="Unknown phase — defaulting to cloud for safety",
            allow_override=True,
        )

    routing = PHASE_ROUTING[phase]

    # For implement phase, further classify by task content
    if phase == SpecPhase.IMPLEMENT and routing.allow_override:
        impl_backend = classify_impl_task(task)
        return PhaseRouting(
            phase=phase,
            backend=impl_backend,
            reason=f"Implementation task classified as {'simple → local' if impl_backend == 'local' else 'complex → cloud'}",
            allow_override=True,
        )

    return routing
