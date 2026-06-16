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
from asharelab.trading import run_offline_paper_day

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


@app.command("llm-smoke")
def llm_smoke() -> None:
    settings = load_settings()
    client = ChatClient(settings.llm)
    payload = client.complete_json(
        "Return compact JSON only.",
        "Return a JSON object with keys status and provider for an A-share paper trading API smoke test.",
    )
    console.print(payload)


@app.command("paper-day")
def paper_day(
    starting_cash: float = typer.Option(100_000.0, help="Virtual starting capital in RMB."),
    portfolio_path: Path = typer.Option(Path("data/paper_portfolio.json"), help="Paper portfolio state."),
    journal_path: Path = typer.Option(Path("data/loop_journal.jsonl"), help="Daily loop journal."),
    allow_repeat: bool = typer.Option(False, help="Allow repeated paper runs for the same date."),
) -> None:
    result = run_offline_paper_day(
        trade_date=date.today(),
        portfolio_path=portfolio_path,
        journal_path=journal_path,
        starting_cash=starting_cash,
        allow_repeat=allow_repeat,
    )
    console.print(f"trade_date: {result.trade_date}")
    console.print(f"starting_equity: {result.starting_equity:.2f}")
    console.print(f"ending_equity: {result.ending_equity:.2f}")
    console.print(f"daily_return: {result.daily_return:.4%}")
    console.print(f"trades: {len(result.trades)}")
    for trade in result.trades:
        console.print(
            f"- {trade.side} {trade.symbol} {trade.quantity} @ {trade.price:.2f}, fees={trade.fees:.2f}"
        )
    console.print(f"lesson: {result.lesson}")
    console.print(f"prompt_adjustment: {result.prompt_adjustment}")


if __name__ == "__main__":
    app()
