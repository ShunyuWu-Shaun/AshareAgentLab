from datetime import date
from pathlib import Path

from asharelab.trading import run_offline_paper_day
from asharelab.trading.rules import AShareRules


def test_a_share_buy_lot_and_price_limits():
    rules = AShareRules()

    assert rules.buy_lot_quantity(10_000, 9.8, 6_000) == 600
    assert rules.is_valid_buy_quantity(600)
    assert not rules.is_valid_buy_quantity(50)
    assert rules.within_price_limit(10.78, 9.8)
    assert not rules.within_price_limit(11.0, 9.8)


def test_offline_paper_day_writes_portfolio_and_journal(tmp_path: Path):
    result = run_offline_paper_day(
        trade_date=date(2026, 6, 16),
        portfolio_path=tmp_path / "portfolio.json",
        journal_path=tmp_path / "journal.jsonl",
        starting_cash=100_000,
    )

    assert result.trades
    assert result.ending_equity > 0
    assert (tmp_path / "portfolio.json").exists()
    assert (tmp_path / "journal.jsonl").read_text(encoding="utf-8")


def test_offline_paper_day_is_not_repeated_by_default(tmp_path: Path):
    kwargs = {
        "trade_date": date(2026, 6, 16),
        "portfolio_path": tmp_path / "portfolio.json",
        "journal_path": tmp_path / "journal.jsonl",
        "starting_cash": 100_000,
    }
    run_offline_paper_day(**kwargs)

    try:
        run_offline_paper_day(**kwargs)
    except RuntimeError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("Expected repeated paper-day run to fail")
