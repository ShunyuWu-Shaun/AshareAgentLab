from __future__ import annotations

from collections import defaultdict
from datetime import date

from asharelab.agents.base import Agent
from asharelab.models import AgentReport, Evidence, MarketEvent, Narrative


class NarrativeScout(Agent):
    name = "NarrativeScout"

    def run(self, events: list[MarketEvent], target_date: date) -> AgentReport:
        grouped: dict[str, list[MarketEvent]] = defaultdict(list)
        for event in events:
            grouped[event.topic].append(event)

        narratives: list[Narrative] = []
        for topic, topic_events in grouped.items():
            score = sum(event.heat * (1 + max(event.sentiment, 0)) for event in topic_events)
            leaders = [event.symbol for event in sorted(topic_events, key=lambda e: e.heat, reverse=True) if event.symbol]
            evidence: list[Evidence] = []
            for event in topic_events[:4]:
                evidence.extend(event.evidence[:1])
            narratives.append(
                Narrative(
                    topic=topic,
                    score=round(score, 3),
                    freshness=min(1.0, len(topic_events) / 5),
                    breadth=len({event.symbol for event in topic_events if event.symbol}),
                    leaders=leaders[:5],
                    summary=f"{topic} 有 {len(topic_events)} 条事件，热度合计 {score:.1f}。",
                    evidence=evidence,
                )
            )

        narratives.sort(key=lambda item: item.score, reverse=True)
        top = narratives[0].topic if narratives else "无明显主题"
        return AgentReport(
            agent_name=self.name,
            report_date=target_date,
            summary=f"最强叙事为 {top}；需要结合涨停扩散和高位反馈确认持续性。",
            narratives=narratives,
        )

