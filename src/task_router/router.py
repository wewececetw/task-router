"""Main orchestrator: classify task → route to appropriate backend → return result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import claude_client, local_client
from .classifier import Classification, TaskComplexity, classify
from .config import RouterConfig
from .speckit import SpecPhase, detect_phase, route_phase

console = Console()


@dataclass
class RouterResult:
    """Result from the router with metadata."""
    content: str
    routed_to: str  # "local" or "cloud"
    model: str
    classification: Classification
    latency_ms: float
    usage: dict = field(default_factory=dict)


class TaskRouter:
    """Routes tasks to local or cloud models based on complexity."""

    def __init__(self, config: RouterConfig | None = None):
        self.config = config or RouterConfig()
        self._local_client = None
        self._claude_client = None

    @property
    def local(self):
        if self._local_client is None:
            self._local_client = local_client.create_client(self.config.omlx)
        return self._local_client

    @property
    def claude(self):
        if self._claude_client is None:
            self._claude_client = claude_client.create_client(self.config.claude)
        return self._claude_client

    def route(
        self,
        task: str,
        system: str | None = None,
        messages: list[dict] | None = None,
        phase: SpecPhase | str | None = None,
    ) -> RouterResult:
        """Classify and route a task to the appropriate backend.

        Args:
            task: The task text
            system: Optional system prompt
            messages: Optional pre-built messages
            phase: Spec Kit phase override (e.g. "plan", "tasks", "implement").
                   If provided, uses phase-based routing instead of generic classifier.
        """
        if messages is None:
            messages = [{"role": "user", "content": task}]

        # Convert string phase to enum
        if isinstance(phase, str):
            try:
                phase = SpecPhase(phase)
            except ValueError:
                phase = None

        # Classify — use Spec Kit phase routing if phase detected
        detected_phase = phase or detect_phase(task)
        classification = classify(task)

        # Determine backend
        if self.config.force_backend:
            backend = self.config.force_backend
        elif detected_phase != SpecPhase.UNKNOWN:
            phase_routing = route_phase(task, detected_phase)
            backend = phase_routing.backend
            # Override classification reason with phase-aware reason
            classification = Classification(
                complexity=TaskComplexity.SIMPLE if backend == "local" else TaskComplexity.COMPLEX,
                confidence=0.85,
                reason=f"[SpecKit:{detected_phase.value}] {phase_routing.reason}",
                matched_rules=[f"speckit_phase:{detected_phase.value}"],
            )
        elif classification.complexity == TaskComplexity.SIMPLE:
            backend = "local"
        else:
            backend = "cloud"

        if self.config.verbose:
            self._print_classification(classification, backend)

        if backend == "local":
            return self._run_local(messages, classification)
        else:
            return self._run_cloud(messages, classification, system)

    def _run_local(
        self, messages: list[dict], classification: Classification
    ) -> RouterResult:
        """Run task on local model via oMLX."""
        try:
            resp = local_client.chat(
                client=self.local,
                messages=messages,
                model=self.config.omlx.model,
            )
            return RouterResult(
                content=resp.content,
                routed_to="local",
                model=resp.model,
                classification=classification,
                latency_ms=resp.latency_ms,
                usage=resp.usage,
            )
        except Exception as e:
            if self.config.verbose:
                console.print(f"[yellow]Local model failed: {e}, falling back to cloud[/yellow]")
            # Fallback to cloud
            return self._run_cloud(messages, classification)

    def _run_cloud(
        self,
        messages: list[dict],
        classification: Classification,
        system: str | None = None,
    ) -> RouterResult:
        """Run task on Claude API."""
        resp = claude_client.chat(
            client=self.claude,
            messages=messages,
            model=self.config.claude.model,
            max_tokens=self.config.claude.max_tokens,
            system=system,
        )
        return RouterResult(
            content=resp.content,
            routed_to="cloud",
            model=resp.model,
            classification=classification,
            latency_ms=resp.latency_ms,
            usage=resp.usage,
        )

    def _print_classification(self, c: Classification, backend: str):
        """Print classification details."""
        table = Table(title="Task Classification", show_header=False)
        table.add_row("Complexity", f"[{'green' if c.complexity == TaskComplexity.SIMPLE else 'red'}]{c.complexity.value}[/]")
        table.add_row("Confidence", f"{c.confidence:.0%}")
        table.add_row("Reason", c.reason)
        table.add_row("Route →", f"[bold]{'🖥️  Local (oMLX)' if backend == 'local' else '☁️  Cloud (Claude)'}[/bold]")
        console.print(table)
