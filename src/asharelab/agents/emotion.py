from __future__ import annotations

from datetime import date

from asharelab.agents.base import Agent
from asharelab.models import AgentReport, MarketEvent, Narrative


class EmotionGauge(Agent):
    name = "EmotionGauge"

    def run(self, events: list[MarketEvent], target_date: date) -> AgentReport:
        if not events:
            return AgentReport(agent_name=self.name, report_date=target_date, summary="没有事件可评估。")

        avg_sentiment = sum(event.sentiment for event in events) / len(events)
        hot_negative = [event for event in events if event.heat >= 6 and event.sentiment < -0.2]
        hot_positive = [event for event in events if event.heat >= 6 and event.sentiment > 0.2]

        state = "偏强"
        if avg_sentiment < -0.2 or len(hot_negative) > len(hot_positive):
            state = "偏弱"
        elif abs(avg_sentiment) <= 0.2:
            state = "分歧"

        warnings = []
        if hot_negative:
            warnings.append("强势股负反馈正在升温，避免只看题材热度。")

        return AgentReport(
            agent_name=self.name,
            report_date=target_date,
            summary=f"短线情绪状态：{state}，平均情绪分 {avg_sentiment:.2f}。",
            narratives=[
                Narrative(
                    topic="短线情绪",
                    score=round(abs(avg_sentiment) * 10 + len(hot_positive) + len(hot_negative), 3),
                    freshness=1.0,
                    breadth=len(events),
                    leaders=[event.symbol for event in hot_positive[:5] if event.symbol],
                    summary=f"正反馈 {len(hot_positive)} 条，负反馈 {len(hot_negative)} 条。",
                )
            ],
            warnings=warnings,
        )

