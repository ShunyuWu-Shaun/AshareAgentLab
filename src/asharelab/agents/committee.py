from __future__ import annotations

from datetime import date

from asharelab.agents.emotion import EmotionGauge
from asharelab.agents.hypothesis import HypothesisBuilder
from asharelab.agents.scout import NarrativeScout
from asharelab.agents.skeptic import Skeptic
from asharelab.llm.client import ChatClient
from asharelab.models import AgentReport, DailyBrief, TradeAction


class AgentCommittee:
    def __init__(self, llm: ChatClient | None = None):
        self.agents = [
            NarrativeScout(llm),
            EmotionGauge(llm),
            HypothesisBuilder(llm),
            Skeptic(llm),
        ]

    def run(self, events, target_date: date) -> DailyBrief:
        reports: list[AgentReport] = [agent.run(events, target_date) for agent in self.agents]
        hypotheses = [hyp for report in reports for hyp in report.hypotheses]

        watchlist: list[TradeAction] = []
        scout_report = next((report for report in reports if report.agent_name == "NarrativeScout"), None)
        if scout_report:
            for narrative in scout_report.narratives[:5]:
                for symbol in narrative.leaders[:2]:
                    watchlist.append(
                        TradeAction(
                            action="watch",
                            symbol=symbol,
                            reason=f"{narrative.topic} 热度靠前，但需等待次日承接确认。",
                            risk_note="只进入观察池，不自动交易。",
                        )
                    )

        return DailyBrief(
            brief_date=target_date,
            summary=f"完成 {len(reports)} 个 agent 的复盘，生成 {len(hypotheses)} 条假设。",
            reports=reports,
            hypotheses=hypotheses,
            watchlist=watchlist,
        )

