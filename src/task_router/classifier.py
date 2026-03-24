"""Rule-based task classifier that determines routing destination."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"


@dataclass
class Classification:
    complexity: TaskComplexity
    confidence: float  # 0.0 - 1.0
    reason: str
    matched_rules: list[str]


# Keywords / patterns that indicate SIMPLE tasks
SIMPLE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("format_code", re.compile(r"\b(format|lint|prettier|black|indent)\b", re.I)),
    ("translate_short", re.compile(r"\b(translat|翻譯|翻译)\b", re.I)),
    ("boilerplate", re.compile(r"\b(boilerplate|template|scaffold|骨架)\b", re.I)),
    ("rename", re.compile(r"\b(rename|重[新命]名)\b", re.I)),
    ("simple_qa", re.compile(r"\b(what is|define|meaning of|是什麼|是什么)\b", re.I)),
    ("summarize", re.compile(r"\b(summarize|summarise|摘要|總結|总结)\b", re.I)),
    ("regex", re.compile(r"\b(regex|regular expression|正則|正则)\b", re.I)),
    ("convert", re.compile(r"\b(convert|transform).*(json|yaml|xml|csv|toml)\b", re.I)),
    ("typo", re.compile(r"\b(typo|spelling|拼寫|拼写)\b", re.I)),
    ("comment", re.compile(r"\b(add comment|加[上個]?註[解釋]|加[上个]?注[解释])\b", re.I)),
]

# Keywords / patterns that indicate COMPLEX tasks
COMPLEX_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("architecture", re.compile(r"\b(architect|design pattern|design.*(?:system|service|platform|app)|microservice|系統設計|系统设计|架構|架构)\b", re.I)),
    ("debug_complex", re.compile(r"\b(debug|troubleshoot|root cause|排[查錯]|排[查错])\b", re.I)),
    ("review", re.compile(r"\b(code review|review.*code|審[查閱]|审[查阅])\b", re.I)),
    ("security", re.compile(r"\b(security|vulnerab|exploit|安全|漏洞)\b", re.I)),
    ("performance", re.compile(r"\b(optimi[zs]e|performance|瓶頸|瓶颈|優化|优化)\b", re.I)),
    ("refactor", re.compile(r"(refactor|重構|重构)", re.I)),
    ("multi_step", re.compile(r"\b(step.by.step|multi.step|plan|策略|計[畫劃]|计[划画])\b", re.I)),
    ("explain_complex", re.compile(r"\b(explain.*how|why does|原理|為什麼|为什么)\b", re.I)),
    ("write_feature", re.compile(r"\b(implement|build|create|develop).*(feature|function|module|api|endpoint)\b", re.I)),
]


def classify(task: str) -> Classification:
    """Classify a task as simple or complex using rule-based heuristics."""
    simple_matches: list[str] = []
    complex_matches: list[str] = []

    for name, pattern in SIMPLE_PATTERNS:
        if pattern.search(task):
            simple_matches.append(name)

    for name, pattern in COMPLEX_PATTERNS:
        if pattern.search(task):
            complex_matches.append(name)

    # Heuristics
    word_count = len(task.split())
    has_code_block = "```" in task or task.count("\n") > 10
    has_multiple_questions = task.count("?") > 1 or task.count("？") > 1

    # Long tasks with code tend to be complex
    if word_count > 200 or has_code_block:
        complex_matches.append("long_or_code")

    if has_multiple_questions:
        complex_matches.append("multi_question")

    # Scoring
    simple_score = len(simple_matches)
    complex_score = len(complex_matches) * 1.5  # weight complex higher

    if complex_score > simple_score:
        confidence = min(0.95, 0.5 + complex_score * 0.15)
        return Classification(
            complexity=TaskComplexity.COMPLEX,
            confidence=confidence,
            reason=f"Matched complex patterns: {', '.join(complex_matches)}",
            matched_rules=complex_matches,
        )
    elif simple_score > 0:
        confidence = min(0.95, 0.5 + simple_score * 0.15)
        return Classification(
            complexity=TaskComplexity.SIMPLE,
            confidence=confidence,
            reason=f"Matched simple patterns: {', '.join(simple_matches)}",
            matched_rules=simple_matches,
        )
    else:
        # Default: if short and no signals, treat as simple; otherwise complex
        if word_count < 50:
            return Classification(
                complexity=TaskComplexity.SIMPLE,
                confidence=0.4,
                reason="Short task with no strong signals, defaulting to simple",
                matched_rules=["default_short"],
            )
        return Classification(
            complexity=TaskComplexity.COMPLEX,
            confidence=0.4,
            reason="No clear signals, defaulting to complex for safety",
            matched_rules=["default_complex"],
        )
