from __future__ import annotations

import os
from datetime import date, datetime, timezone

from asharelab.data.sources import DataSource, _event_id
from asharelab.models import Evidence, MarketEvent


class TushareSource(DataSource):
    """Thin adapter placeholder for Tushare Pro.

    The first implementation only normalizes daily quote movers. More endpoints
    should be added as small methods rather than one large all-purpose adapter.
    """

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("TUSHARE_TOKEN", "")
        if not self.token:
            raise RuntimeError("TUSHARE_TOKEN is required")

    def load_events(self, target_date: date) -> list[MarketEvent]:
        import tushare as ts

        pro = ts.pro_api(self.token)
        trade_date = target_date.strftime("%Y%m%d")
        daily = pro.daily(trade_date=trade_date)
        if daily.empty:
            return []

        top = daily.sort_values("pct_chg", ascending=False).head(20)
        events: list[MarketEvent] = []
        for _, row in top.iterrows():
            symbol = str(row["ts_code"])
            pct = float(row.get("pct_chg", 0.0))
            events.append(
                MarketEvent(
                    event_id=_event_id(trade_date, symbol, "daily_mover"),
                    event_date=target_date,
                    topic="日内强势股",
                    event_type="daily_mover",
                    symbol=symbol,
                    summary=f"{symbol} 当日涨跌幅 {pct:.2f}%。",
                    sentiment=max(min(pct / 10.0, 1.0), -1.0),
                    heat=abs(pct),
                    evidence=[
                        Evidence(
                            source="tushare.daily",
                            summary=f"Tushare daily row for {symbol}",
                            observed_at=datetime.now(timezone.utc),
                        )
                    ],
                    metadata={"pct_chg": pct},
                )
            )
        return events
