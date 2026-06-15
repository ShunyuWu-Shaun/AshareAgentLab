from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from hashlib import sha1
from typing import Iterable

from asharelab.models import Evidence, MarketEvent


class DataSource(ABC):
    @abstractmethod
    def load_events(self, target_date: date) -> list[MarketEvent]:
        """Return market events already normalized for agent consumption."""


def _event_id(*parts: str) -> str:
    return sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]


class MockAshareSource(DataSource):
    """Deterministic seed data used by tests and early framework work."""

    def load_events(self, target_date: date) -> list[MarketEvent]:
        samples = [
            {
                "topic": "低空经济",
                "event_type": "limit_up_cluster",
                "summary": "板块出现多只涨停，低位补涨标的开始扩散。",
                "symbol": "000001",
                "name": "样例低空龙头",
                "sentiment": 0.72,
                "heat": 8.5,
            },
            {
                "topic": "AI应用",
                "event_type": "news_catalyst",
                "summary": "应用侧新闻密集，但高位股分歧加大。",
                "symbol": "000002",
                "name": "样例AI高位股",
                "sentiment": 0.28,
                "heat": 6.2,
            },
            {
                "topic": "风险反馈",
                "event_type": "failed_limit_up",
                "summary": "昨日强势股炸板率上升，短线资金开始谨慎。",
                "symbol": "000003",
                "name": "样例情绪锚",
                "sentiment": -0.55,
                "heat": 7.1,
            },
        ]
        return [
            MarketEvent(
                event_id=_event_id(str(target_date), item["topic"], item["symbol"]),
                event_date=target_date,
                evidence=[
                    Evidence(
                        source="mock",
                        summary="Offline fixture; replace with Tushare, AKShare, or crawler evidence.",
                        observed_at=datetime.now(timezone.utc),
                    )
                ],
                **item,
            )
            for item in samples
        ]


class CompositeSource(DataSource):
    def __init__(self, sources: Iterable[DataSource]):
        self.sources = list(sources)

    def load_events(self, target_date: date) -> list[MarketEvent]:
        events: list[MarketEvent] = []
        for source in self.sources:
            events.extend(source.load_events(target_date))
        return events
