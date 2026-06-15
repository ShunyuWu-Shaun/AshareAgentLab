from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from asharelab.llm.client import ChatClient
from asharelab.models import AgentReport, MarketEvent


class Agent(ABC):
    name: str

    def __init__(self, llm: ChatClient | None = None):
        self.llm = llm

    @abstractmethod
    def run(self, events: list[MarketEvent], target_date: date) -> AgentReport:
        """Analyze normalized market events and return a report."""


def summarize_events(events: list[MarketEvent], limit: int = 12) -> str:
    lines = []
    for event in events[:limit]:
        label = f"{event.symbol or '-'} {event.name or ''}".strip()
        lines.append(
            f"- [{event.topic}/{event.event_type}] {label}: {event.summary} "
            f"(sentiment={event.sentiment:.2f}, heat={event.heat:.1f})"
        )
    return "\n".join(lines)

