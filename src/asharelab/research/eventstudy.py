from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class EventStudyResult:
    sample_size: int
    mean_forward_return: float
    win_rate: float
    max_loss: float


def simple_forward_return_study(
    events: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    horizon_days: int = 1,
) -> EventStudyResult:
    """Evaluate event-date close to future close returns.

    Expected columns:
    events: symbol, event_date
    prices: symbol, date, close
    """

    if events.empty:
        return EventStudyResult(sample_size=0, mean_forward_return=0.0, win_rate=0.0, max_loss=0.0)

    price_map = {
        symbol: group.sort_values("date").reset_index(drop=True)
        for symbol, group in prices.groupby("symbol")
    }
    returns: list[float] = []
    for _, event in events.iterrows():
        symbol = event["symbol"]
        frame = price_map.get(symbol)
        if frame is None:
            continue
        matches = frame.index[frame["date"] == event["event_date"]].tolist()
        if not matches:
            continue
        idx = matches[0]
        future_idx = idx + horizon_days
        if future_idx >= len(frame):
            continue
        start = float(frame.loc[idx, "close"])
        end = float(frame.loc[future_idx, "close"])
        if start > 0:
            returns.append(end / start - 1)

    if not returns:
        return EventStudyResult(sample_size=0, mean_forward_return=0.0, win_rate=0.0, max_loss=0.0)
    return EventStudyResult(
        sample_size=len(returns),
        mean_forward_return=sum(returns) / len(returns),
        win_rate=sum(ret > 0 for ret in returns) / len(returns),
        max_loss=min(returns),
    )

