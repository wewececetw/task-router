"""Workflow-aware phase routing.

Supports pluggable workflow toolkits (vibe-lens, Spec Kit, or custom).
Maps workflow phases to routing decisions:
- Deep reasoning phases → cloud (Claude)
- Structured output phases → local (oMLX)
- Implementation → depends on individual task complexity
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class PhaseRouting:
    """Routing decision for a workflow phase."""
    phase: str
    backend: str  # "local" or "cloud"
    reason: str
    allow_override: bool = False  # Can task-level complexity override?


@dataclass
class WorkflowConfig:
    """Pluggable workflow definition with phase routing."""
    name: str
    phases: dict[str, PhaseRouting] = field(default_factory=dict)
    detectors: list[tuple[str, re.Pattern]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Implementation task classifiers (workflow-agnostic)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Workflow presets
# ---------------------------------------------------------------------------

def vibelens_workflow() -> WorkflowConfig:
    """Vibe Lens (Spec-Driven Development) workflow preset."""
    phases = {
        "constitution": PhaseRouting(
            phase="constitution", backend="cloud",
            reason="定義專案原則 — 需要深度推理",
        ),
        "specify": PhaseRouting(
            phase="specify", backend="cloud",
            reason="需求分析需要理解使用者故事",
        ),
        "clarify": PhaseRouting(
            phase="clarify", backend="cloud",
            reason="釐清需要理解上下文找出缺口",
        ),
        "plan": PhaseRouting(
            phase="plan", backend="cloud",
            reason="架構決策需要強推理能力",
        ),
        "tasks": PhaseRouting(
            phase="tasks", backend="local",
            reason="結構化轉換，從 plan 拆解任務",
        ),
        "implement": PhaseRouting(
            phase="implement", backend="local",
            reason="依個別任務複雜度決定",
            allow_override=True,
        ),
        "analyze": PhaseRouting(
            phase="analyze", backend="local",
            reason="一致性檢查是模式匹配工作",
        ),
        "checklist": PhaseRouting(
            phase="checklist", backend="local",
            reason="結構化輸出",
        ),
        "gate": PhaseRouting(
            phase="gate", backend="cloud",
            reason="理解關卡需要推理判斷正確性",
        ),
        "digest": PhaseRouting(
            phase="digest", backend="local",
            reason="從現有產出物做結構化摘要",
        ),
        "export": PhaseRouting(
            phase="export", backend="local",
            reason="結構化報告格式轉換",
        ),
        "review_artifact": PhaseRouting(
            phase="review_artifact", backend="local",
            reason="方法論檢查清單比對",
        ),
    }

    detectors = [
        ("constitution", re.compile(r"constitution|核心原則|core.?principles", re.I)),
        ("checklist",    re.compile(r"checklist|檢查清單|quality.?check", re.I)),
        ("tasks",        re.compile(r"tasks?\b|task.?list|任務列表|task.?breakdown", re.I)),
        ("analyze",      re.compile(r"analy[zs]e|一致性|consistency.?check", re.I)),
        ("implement",    re.compile(r"implement|執行|實作|write.?code|coding", re.I)),
        ("clarify",      re.compile(r"clarify|釐清|澄清|underspecified", re.I)),
        ("specify",      re.compile(r"spec(?:ify)?(?:\s|$)|需求|requirement|user.?stor", re.I)),
        ("plan",         re.compile(r"plan\b|implementation.?plan|架構|architecture.?design", re.I)),
        ("gate",         re.compile(r"gate|理解關|comprehension.?check", re.I)),
        ("digest",       re.compile(r"digest|商業邏輯|business.?logic.?summary", re.I)),
        ("export",       re.compile(r"export|匯出|stakeholder.?report", re.I)),
        ("review_artifact", re.compile(r"review.?artifact|審閱產出|artifact.?review", re.I)),
    ]

    return WorkflowConfig(name="vibe-lens", phases=phases, detectors=detectors)


def speckit_workflow() -> WorkflowConfig:
    """Spec Kit workflow preset (subset of vibe-lens phases)."""
    phases = {
        "constitution": PhaseRouting(
            phase="constitution", backend="cloud",
            reason="Constitution defines project-wide principles — needs deep reasoning",
        ),
        "specify": PhaseRouting(
            phase="specify", backend="cloud",
            reason="Specification requires understanding requirements and user stories",
        ),
        "clarify": PhaseRouting(
            phase="clarify", backend="cloud",
            reason="Clarification needs contextual understanding to find gaps",
        ),
        "plan": PhaseRouting(
            phase="plan", backend="cloud",
            reason="Architecture and design decisions need strong reasoning",
        ),
        "tasks": PhaseRouting(
            phase="tasks", backend="local",
            reason="Task breakdown is structured transformation from plan",
        ),
        "implement": PhaseRouting(
            phase="implement", backend="local",
            reason="Implementation routes by individual task complexity",
            allow_override=True,
        ),
        "analyze": PhaseRouting(
            phase="analyze", backend="local",
            reason="Consistency checking is pattern-matching work",
        ),
        "checklist": PhaseRouting(
            phase="checklist", backend="local",
            reason="Checklist generation is structured output",
        ),
    }

    detectors = [
        ("constitution", re.compile(r"(?:speckit\.)?constitution|核心原則|core.?principles", re.I)),
        ("checklist",    re.compile(r"(?:speckit\.)?checklist|檢查清單|quality.?check", re.I)),
        ("tasks",        re.compile(r"(?:speckit\.)?tasks?\b|task.?list|任務列表|task.?breakdown", re.I)),
        ("analyze",      re.compile(r"(?:speckit\.)?analy[zs]e|一致性|consistency.?check", re.I)),
        ("implement",    re.compile(r"(?:speckit\.)?implement|執行|實作|write.?code|coding", re.I)),
        ("clarify",      re.compile(r"(?:speckit\.)?clarify|釐清|澄清|underspecified", re.I)),
        ("specify",      re.compile(r"(?:speckit\.)?spec(?:ify)?(?:\s|$)|需求|requirement|user.?stor", re.I)),
        ("plan",         re.compile(r"(?:speckit\.)?plan\b|implementation.?plan|架構|architecture.?design", re.I)),
    ]

    return WorkflowConfig(name="speckit", phases=phases, detectors=detectors)


# ---------------------------------------------------------------------------
# Workflow registry
# ---------------------------------------------------------------------------

WORKFLOW_PRESETS: dict[str, callable] = {
    "vibelens": vibelens_workflow,
    "vibe-lens": vibelens_workflow,
    "speckit": speckit_workflow,
    "spec-kit": speckit_workflow,
}


def get_workflow(name: str = "vibelens") -> WorkflowConfig:
    """Get a workflow config by name."""
    factory = WORKFLOW_PRESETS.get(name)
    if factory is None:
        raise ValueError(f"Unknown workflow: {name!r}. Available: {', '.join(WORKFLOW_PRESETS)}")
    return factory()


# ---------------------------------------------------------------------------
# Phase detection & routing
# ---------------------------------------------------------------------------

def detect_phase(task: str, config: WorkflowConfig | None = None) -> str:
    """Detect which workflow phase a task belongs to."""
    if config is None:
        config = vibelens_workflow()
    for phase, pattern in config.detectors:
        if pattern.search(task):
            return phase
    return "unknown"


def classify_impl_task(task_description: str) -> str:
    """For implementation phase, decide if a specific task is simple or complex.

    Returns "local" or "cloud".
    """
    simple_score = sum(1 for _, p in SIMPLE_IMPL_PATTERNS if p.search(task_description))
    complex_score = sum(1.5 for _, p in COMPLEX_IMPL_PATTERNS if p.search(task_description))

    if complex_score > simple_score:
        return "cloud"
    return "local"


def route_phase(task: str, config: WorkflowConfig | None = None, phase: str | None = None) -> PhaseRouting:
    """Determine routing for a task based on its workflow phase.

    Args:
        task: The task description or prompt
        config: Workflow config to use. Defaults to vibe-lens.
        phase: Explicit phase override. If None, auto-detect from task text.

    Returns:
        PhaseRouting with backend decision
    """
    if config is None:
        config = vibelens_workflow()

    if phase is None:
        phase = detect_phase(task, config)

    if phase == "unknown" or phase not in config.phases:
        return PhaseRouting(
            phase="unknown",
            backend="cloud",
            reason="Unknown phase — defaulting to cloud for safety",
            allow_override=True,
        )

    routing = config.phases[phase]

    # For implement phase, further classify by task content
    if phase == "implement" and routing.allow_override:
        impl_backend = classify_impl_task(task)
        return PhaseRouting(
            phase=phase,
            backend=impl_backend,
            reason=f"Implementation task classified as {'simple → local' if impl_backend == 'local' else 'complex → cloud'}",
            allow_override=True,
        )

    return routing
