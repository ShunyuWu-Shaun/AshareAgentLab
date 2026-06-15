from __future__ import annotations

from datetime import UTC, date, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Evidence(BaseModel):
    """A small, auditable unit of support for an agent claim."""

    source: str
    summary: str
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    url: str | None = None
    confidence: Confidence = Confidence.MEDIUM
    metadata: dict[str, Any] = Field(default_factory=dict)


class MarketEvent(BaseModel):
    event_id: str
    event_date: date
    topic: str
    event_type: str
    summary: str
    symbol: str | None = None
    name: str | None = None
    sentiment: float = Field(0.0, ge=-1.0, le=1.0)
    heat: float = Field(0.0, ge=0.0)
    evidence: list[Evidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Narrative(BaseModel):
    topic: str
    score: float = Field(0.0, ge=0.0)
    freshness: float = Field(0.0, ge=0.0, le=1.0)
    breadth: int = 0
    leaders: list[str] = Field(default_factory=list)
    summary: str = ""
    evidence: list[Evidence] = Field(default_factory=list)


class Hypothesis(BaseModel):
    title: str
    thesis: str
    invalidation: str
    required_observations: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM
    evidence: list[Evidence] = Field(default_factory=list)


class AgentReport(BaseModel):
    agent_name: str
    report_date: date = Field(default_factory=date.today)
    summary: str
    narratives: list[Narrative] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TradeAction(BaseModel):
    """A research action, not a broker order."""

    action: Literal["watch", "ignore", "review", "paper_buy", "paper_sell"]
    symbol: str
    reason: str
    risk_note: str
    confidence: Confidence = Confidence.LOW


class DailyBrief(BaseModel):
    brief_date: date = Field(default_factory=date.today)
    summary: str
    reports: list[AgentReport] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    watchlist: list[TradeAction] = Field(default_factory=list)
