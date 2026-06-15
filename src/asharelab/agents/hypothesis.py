from __future__ import annotations

from datetime import date

from asharelab.agents.base import Agent
from asharelab.models import AgentReport, Confidence, Hypothesis, MarketEvent


class HypothesisBuilder(Agent):
    name = "HypothesisBuilder"

    def run(self, events: list[MarketEvent], target_date: date) -> AgentReport:
        by_topic: dict[str, list[MarketEvent]] = {}
        for event in events:
            by_topic.setdefault(event.topic, []).append(event)

        hypotheses: list[Hypothesis] = []
        for topic, topic_events in by_topic.items():
            positive = [event for event in topic_events if event.sentiment > 0.2]
            negative = [event for event in topic_events if event.sentiment < -0.2]
            if not positive:
                continue

            hypotheses.append(
                Hypothesis(
                    title=f"{topic} 叙事扩散假设",
                    thesis=(
                        f"若 {topic} 的前排继续保持强承接，且后排补涨数量增加，"
                        "则主题可能处于扩散阶段。"
                    ),
                    invalidation=(
                        "龙头断板后出现明显负反馈，或后排冲高回落且板块成交额萎缩。"
                    ),
                    required_observations=[
                        "次日竞价强度",
                        "板块内涨停/炸板数量",
                        "前排成交额和换手结构",
                        "高位股负反馈是否扩散",
                    ],
                    tags=[topic, "narrative", "event-study"],
                    confidence=Confidence.MEDIUM if len(negative) == 0 else Confidence.LOW,
                    evidence=[evidence for event in topic_events[:3] for evidence in event.evidence[:1]],
                )
            )

        return AgentReport(
            agent_name=self.name,
            report_date=target_date,
            summary=f"生成 {len(hypotheses)} 条可检验假设。",
            hypotheses=hypotheses,
        )

