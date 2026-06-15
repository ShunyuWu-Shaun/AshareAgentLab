from __future__ import annotations

from datetime import date

from asharelab.agents.base import Agent
from asharelab.models import AgentReport, MarketEvent


class Skeptic(Agent):
    name = "Skeptic"

    def run(self, events: list[MarketEvent], target_date: date) -> AgentReport:
        warnings: list[str] = []
        if not events:
            warnings.append("没有输入事件，任何结论都不可用。")

        if any(not event.evidence for event in events):
            warnings.append("部分事件缺少证据来源，需要补充原始链接或数据快照。")

        if len({event.topic for event in events}) <= 1 and len(events) > 3:
            warnings.append("主题过于集中，可能遗漏市场反证和轮动风险。")

        if any(event.event_type in {"hot_rank", "news_catalyst"} for event in events):
            warnings.append("热榜和新闻只能证明注意力，不等同于可交易优势。")

        summary = "未发现硬性阻断问题。" if not warnings else "存在需要复核的证据和偏差风险。"
        return AgentReport(agent_name=self.name, report_date=target_date, summary=summary, warnings=warnings)

