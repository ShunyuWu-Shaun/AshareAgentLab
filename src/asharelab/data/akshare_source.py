from __future__ import annotations

from datetime import date, datetime, timezone

from asharelab.data.sources import DataSource, _event_id
from asharelab.models import Evidence, MarketEvent


class AkshareSource(DataSource):
    """AKShare adapter for public A-share heat and money-flow style data."""

    def load_events(self, target_date: date) -> list[MarketEvent]:
        import akshare as ak

        try:
            hot = ak.stock_hot_rank_em()
        except Exception as exc:  # AKShare endpoints can change; keep failure local.
            raise RuntimeError(f"AKShare hot rank failed: {exc}") from exc

        events: list[MarketEvent] = []
        for _, row in hot.head(50).iterrows():
            symbol = str(row.get("代码", ""))
            name = str(row.get("股票名称", row.get("名称", "")))
            heat = float(row.get("当前排名", 50))
            events.append(
                MarketEvent(
                    event_id=_event_id(str(target_date), symbol, "hot_rank"),
                    event_date=target_date,
                    topic="市场热榜",
                    event_type="hot_rank",
                    symbol=symbol,
                    name=name,
                    summary=f"{name} 出现在东方财富热榜。",
                    sentiment=0.2,
                    heat=max(0.0, 100.0 - heat),
                    evidence=[
                        Evidence(
                            source="akshare.stock_hot_rank_em",
                            summary="东方财富股票热度榜。",
                            observed_at=datetime.now(timezone.utc),
                        )
                    ],
                )
            )
        return events
