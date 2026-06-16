from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from asharelab.agents import AgentCommittee
from asharelab.data import MockAshareSource
from asharelab.models import DailyBrief
from asharelab.trading.portfolio import Portfolio, Trade
from asharelab.trading.rules import AShareRules


@dataclass(frozen=True)
class MockQuote:
    symbol: str
    name: str
    previous_close: float
    decision_price: float
    close_price: float


@dataclass(frozen=True)
class DailyLoopResult:
    trade_date: str
    starting_equity: float
    ending_equity: float
    daily_return: float
    trades: list[Trade]
    lesson: str
    prompt_adjustment: str
    brief: DailyBrief


MOCK_QUOTES = {
    "000001": MockQuote("000001", "样例低空龙头", 9.80, 10.20, 10.58),
    "000002": MockQuote("000002", "样例AI高位股", 15.10, 15.55, 15.20),
    "000003": MockQuote("000003", "样例情绪锚", 8.90, 8.75, 8.52),
}


def _reflect(daily_return: float, brief: DailyBrief) -> tuple[str, str]:
    if daily_return < -0.01:
        return (
            "当日亏损超过 1%，说明入场确认不足或风险反馈权重过低。",
            "下个版本 prompt 必须要求：负反馈主题不得进入买入候选；单票仓位降至 15%；需要两个以上确认信号。",
        )
    if daily_return > 0.01:
        return (
            "当日收益超过 1%，叙事扩散假设得到初步正反馈，但仍需防止过拟合单日样本。",
            "下个版本 prompt 保持叙事扩散逻辑，同时增加次日冲高回落和炸板率检查。",
        )
    warning_count = sum(len(report.warnings) for report in brief.reports)
    return (
        f"当日收益接近持平，系统识别到 {warning_count} 条风险提醒。",
        "下个版本 prompt 强化风险提醒到仓位映射，避免所有 watchlist 都被等权处理。",
    )


def run_offline_paper_day(
    *,
    trade_date: date,
    portfolio_path: Path,
    journal_path: Path,
    starting_cash: float = 100_000.0,
    max_position_fraction: float = 0.20,
    allow_repeat: bool = False,
) -> DailyLoopResult:
    if not allow_repeat and _journal_has_date(journal_path, trade_date.isoformat()):
        raise RuntimeError(
            f"Paper loop for {trade_date.isoformat()} already exists. "
            "Use allow_repeat=True only for controlled experiments."
        )

    rules = AShareRules()
    portfolio = Portfolio.load(portfolio_path, starting_cash)
    portfolio.roll_t_plus_one(trade_date)
    portfolio.update_prices({symbol: quote.decision_price for symbol, quote in MOCK_QUOTES.items()})
    starting_equity = portfolio.equity()

    events = MockAshareSource().load_events(trade_date)
    brief = AgentCommittee().run(events, trade_date)

    trades: list[Trade] = []
    risk_symbols = {event.symbol for event in events if event.sentiment < -0.2}
    max_position_value = starting_equity * max_position_fraction

    for item in brief.watchlist:
        if item.symbol in risk_symbols:
            continue
        quote = MOCK_QUOTES.get(item.symbol)
        if quote is None:
            continue
        if not rules.within_price_limit(quote.decision_price, quote.previous_close):
            continue
        quantity = rules.buy_lot_quantity(portfolio.cash, quote.decision_price, max_position_value)
        trade = portfolio.buy(
            item.symbol,
            quote.name,
            quantity,
            quote.decision_price,
            trade_date,
            item.reason,
            rules,
        )
        if trade:
            trades.append(trade)

    portfolio.update_prices({symbol: quote.close_price for symbol, quote in MOCK_QUOTES.items()})
    ending_equity = portfolio.equity()
    daily_return = 0.0 if starting_equity == 0 else ending_equity / starting_equity - 1
    lesson, prompt_adjustment = _reflect(daily_return, brief)

    result = DailyLoopResult(
        trade_date=trade_date.isoformat(),
        starting_equity=round(starting_equity, 2),
        ending_equity=round(ending_equity, 2),
        daily_return=round(daily_return, 6),
        trades=trades,
        lesson=lesson,
        prompt_adjustment=prompt_adjustment,
        brief=brief,
    )
    portfolio.save(portfolio_path)
    journal_path.parent.mkdir(parents=True, exist_ok=True)
    with journal_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(result), ensure_ascii=False, default=str) + "\n")
    return result


def _journal_has_date(path: Path, trade_date: str) -> bool:
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if payload.get("trade_date") == trade_date:
                return True
    return False
