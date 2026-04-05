"""CLI entry point for task-router."""

from __future__ import annotations

import os
import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .classifier import classify, TaskComplexity
from .config import RouterConfig, ClaudeConfig, OMLXConfig
from .router import TaskRouter
from .workflow import get_workflow, detect_phase, route_phase

app = typer.Typer(
    name="task-router",
    help="Route tasks to local models (oMLX) or Claude API based on complexity.",
)
console = Console()


def _build_config(
    claude_key: str | None,
    claude_model: str,
    omlx_url: str,
    omlx_model: str,
    omlx_key: str | None,
    verbose: bool,
    force: str | None,
    workflow: str = "speckit",
) -> RouterConfig:
    api_key = claude_key or os.environ.get("ANTHROPIC_API_KEY", "")
    omlx_api_key = omlx_key or os.environ.get("OMLX_API_KEY", "")
    return RouterConfig(
        claude=ClaudeConfig(api_key=api_key, model=claude_model),
        omlx=OMLXConfig(base_url=omlx_url, model=omlx_model, api_key=omlx_api_key),
        verbose=verbose,
        force_backend=force,
        workflow=workflow,
    )


@app.command()
def ask(
    task: str = typer.Argument(..., help="The task or question to route"),
    claude_key: str | None = typer.Option(None, "--key", "-k", envvar="ANTHROPIC_API_KEY", help="Claude API key or OAuth token"),
    claude_model: str = typer.Option("claude-sonnet-4-20250514", "--claude-model", help="Claude model to use"),
    omlx_url: str = typer.Option("http://127.0.0.1:9000/v1", "--omlx-url", help="oMLX server URL"),
    omlx_model: str = typer.Option("Qwen3.5-9B-MLX-4bit", "--omlx-model", help="Local model name"),
    omlx_key: str | None = typer.Option(None, "--omlx-key", envvar="OMLX_API_KEY", help="oMLX API key"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show classification details"),
    force: str | None = typer.Option(None, "--force", "-f", help="Force routing to 'local' or 'cloud'"),
    phase: str | None = typer.Option(None, "--phase", "-p", help="Workflow phase override (e.g. plan, tasks, implement)"),
    workflow: str = typer.Option("speckit", "--workflow", "-w", help="Workflow preset: speckit"),
    system: str | None = typer.Option(None, "--system", "-s", help="System prompt"),
):
    """Send a task and let the router decide where to run it."""
    config = _build_config(claude_key, claude_model, omlx_url, omlx_model, omlx_key, verbose, force, workflow)
    router = TaskRouter(config)

    try:
        result = router.route(task, system=system, phase=phase)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Print result
    backend_label = "Local (oMLX)" if result.routed_to == "local" else "Cloud (Claude)"
    console.print(Panel(
        result.content,
        title=f"[bold]{backend_label}[/bold] — {result.model}",
        subtitle=f"{result.latency_ms:.0f}ms | {result.classification.complexity.value}",
        border_style="green" if result.routed_to == "local" else "blue",
    ))


@app.command()
def classify_task(
    task: str = typer.Argument(..., help="Task to classify"),
):
    """Classify a task without executing it (dry run)."""
    c = classify(task)
    table = Table(title="Classification Result", show_header=False)
    color = "green" if c.complexity == TaskComplexity.SIMPLE else "red"
    table.add_row("Complexity", f"[{color}]{c.complexity.value}[/{color}]")
    table.add_row("Confidence", f"{c.confidence:.0%}")
    table.add_row("Reason", c.reason)
    table.add_row("Rules", ", ".join(c.matched_rules))
    route = "Local (oMLX)" if c.complexity == TaskComplexity.SIMPLE else "Cloud (Claude)"
    table.add_row("Would route →", f"[bold]{route}[/bold]")
    console.print(table)


@app.command()
def phases(
    task_file: str | None = typer.Argument(None, help="Path to tasks.md file to analyze"),
    workflow: str = typer.Option("speckit", "--workflow", "-w", help="Workflow preset: speckit"),
):
    """Show workflow phase routing table, or analyze a tasks.md file."""
    wf = get_workflow(workflow)

    if task_file is None:
        # Show the routing table
        table = Table(title=f"Phase Routing ({wf.name})", show_header=True)
        table.add_column("Phase", style="bold")
        table.add_column("Backend", style="bold")
        table.add_column("Reason")

        for phase_name, routing in wf.phases.items():
            color = "green" if routing.backend == "local" else "blue"
            table.add_row(
                phase_name,
                f"[{color}]{routing.backend}[/{color}]",
                routing.reason,
            )
        console.print(table)
        return

    # Analyze a tasks.md file
    import re as _re
    from pathlib import Path

    path = Path(task_file)
    if not path.exists():
        console.print(f"[red]File not found: {task_file}[/red]")
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")
    task_pattern = _re.compile(r"- \[ \] (T\d+.*)")
    tasks = task_pattern.findall(content)

    if not tasks:
        console.print("[yellow]No tasks found in file[/yellow]")
        raise typer.Exit(0)

    table = Table(title=f"Task Routing Analysis: {path.name}", show_header=True)
    table.add_column("Task ID", style="bold", width=8)
    table.add_column("Description", width=50)
    table.add_column("Route", width=15)

    local_count = 0
    cloud_count = 0

    for task_line in tasks:
        routing = route_phase(task_line, wf, "implement")
        color = "green" if routing.backend == "local" else "blue"
        # Extract task ID
        id_match = _re.match(r"(T\d+)", task_line)
        task_id = id_match.group(1) if id_match else "?"
        desc = task_line[len(task_id):].strip() if id_match else task_line

        if routing.backend == "local":
            local_count += 1
        else:
            cloud_count += 1

        table.add_row(
            task_id,
            desc[:50],
            f"[{color}]{'🖥️  local' if routing.backend == 'local' else '☁️  cloud'}[/{color}]",
        )

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {local_count} local (oMLX) | {cloud_count} cloud (Claude) | {local_count + cloud_count} total")
    if local_count + cloud_count > 0:
        pct = local_count / (local_count + cloud_count) * 100
        console.print(f"[bold green]{pct:.0f}% of tasks can run locally[/bold green] — saving API cost 💰")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h"),
    port: int = typer.Option(8080, "--port", "-p"),
    claude_key: str | None = typer.Option(None, "--key", "-k", envvar="ANTHROPIC_API_KEY"),
    claude_model: str = typer.Option("claude-sonnet-4-20250514", "--claude-model"),
    omlx_url: str = typer.Option("http://127.0.0.1:9000/v1", "--omlx-url"),
    omlx_model: str = typer.Option("Qwen3.5-9B-MLX-4bit", "--omlx-model"),
    omlx_key: str | None = typer.Option(None, "--omlx-key", envvar="OMLX_API_KEY"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Start the router as an OpenAI-compatible API server."""
    import uvicorn
    from .server import create_app

    config = _build_config(claude_key, claude_model, omlx_url, omlx_model, omlx_key, verbose, None)
    app_instance = create_app(config)
    console.print(f"[bold green]Task Router server starting on {host}:{port}[/bold green]")
    uvicorn.run(app_instance, host=host, port=port)


@app.command()
def demo():
    """Run demo classifications on sample tasks."""
    tasks = [
        "Format this Python code with black",
        "翻譯 hello world 成中文",
        "Help me debug why my API returns 500 errors when handling concurrent requests",
        "Rename the variable 'x' to 'user_count'",
        "Design a microservice architecture for an e-commerce platform",
        "Convert this JSON to YAML",
        "Review this code for security vulnerabilities",
        "What is a list comprehension?",
        "Optimize the database queries in our user service, they're causing N+1 problems",
    ]

    table = Table(title="Demo: Task Classification")
    table.add_column("Task", style="white", max_width=50)
    table.add_column("Complexity", justify="center")
    table.add_column("Confidence", justify="center")
    table.add_column("Route", justify="center")

    for task in tasks:
        c = classify(task)
        color = "green" if c.complexity == TaskComplexity.SIMPLE else "red"
        route = "Local" if c.complexity == TaskComplexity.SIMPLE else "Cloud"
        table.add_row(
            task[:50],
            f"[{color}]{c.complexity.value}[/{color}]",
            f"{c.confidence:.0%}",
            f"[{color}]{route}[/{color}]",
        )

    console.print(table)


if __name__ == "__main__":
    app()
