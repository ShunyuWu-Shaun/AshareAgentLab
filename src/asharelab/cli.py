from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from asharelab.agents import AgentCommittee
from asharelab.config import load_settings
from asharelab.data import MockAshareSource
from asharelab.llm.budget import TokenUsage, estimate_cost_cny
from asharelab.llm.client import ChatClient
from asharelab.memory import MarketMemory
from asharelab.reports import render_daily_brief

app = typer.Typer(help="AshareAgentLab command line tools.")
console = Console()


@app.command()
def doctor() -> None:
    settings = load_settings()
    console.print("[bold]AshareAgentLab[/bold]")
    console.print(f"provider: {settings.llm.provider}")
    console.print(f"model: {settings.llm.model}")
    console.print(f"monthly budget: {settings.llm.monthly_budget_cny:.2f} RMB")
    console.print(f"memory: {settings.memory.sqlite_path}")


@app.command()
def estimate(
    provider: str = typer.Option("deepseek", help="Provider key in the pricing registry."),
    input_tokens: int = typer.Option(20_000_000, help="Monthly input tokens."),
    output_tokens: int = typer.Option(5_000_000, help="Monthly output tokens."),
    cached_input_tokens: int = typer.Option(0, help="Monthly cached input tokens."),
) -> None:
    cost = estimate_cost_cny(
        provider,
        TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached_input_tokens,
        ),
    )
    console.print(f"{provider}: estimated monthly cost = [bold]{cost:.2f} RMB[/bold]")


@app.command()
def demo(
    offline: bool = typer.Option(True, help="Use deterministic mock data."),
    output: Path | None = typer.Option(None, help="Optional markdown output path."),
) -> None:
    if not offline:
        raise typer.BadParameter("Only offline demo is implemented in the starter framework.")

    settings = load_settings()
    source = MockAshareSource()
    events = source.load_events(date.today())
    memory = MarketMemory(settings.memory.sqlite_path)
    memory.add_events(events)

    committee = AgentCommittee(ChatClient(settings.llm))
    brief = committee.run(events, date.today())
    memory.add_hypotheses(brief.hypotheses)
    for report in brief.reports:
        memory.add_report(report)

    markdown = render_daily_brief(brief)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        console.print(f"wrote {output}")
    else:
        console.print(markdown)


if __name__ == "__main__":
    app()

