from __future__ import annotations

from asharelab.models import DailyBrief


def render_daily_brief(brief: DailyBrief) -> str:
    lines = [
        f"# A-share Agent Brief - {brief.brief_date.isoformat()}",
        "",
        brief.summary,
        "",
        "## Agent Reports",
    ]
    for report in brief.reports:
        lines.extend([f"### {report.agent_name}", report.summary, ""])
        for warning in report.warnings:
            lines.append(f"- Warning: {warning}")
        for narrative in report.narratives[:5]:
            leaders = ", ".join(narrative.leaders) if narrative.leaders else "-"
            lines.append(f"- {narrative.topic}: score={narrative.score:.2f}, leaders={leaders}")
        if report.narratives or report.warnings:
            lines.append("")

    lines.append("## Hypotheses")
    if not brief.hypotheses:
        lines.append("- No hypotheses generated.")
    for hyp in brief.hypotheses:
        lines.extend(
            [
                f"### {hyp.title}",
                f"- Thesis: {hyp.thesis}",
                f"- Invalidation: {hyp.invalidation}",
                f"- Observations: {', '.join(hyp.required_observations)}",
                "",
            ]
        )

    lines.append("## Watchlist")
    if not brief.watchlist:
        lines.append("- Empty.")
    for item in brief.watchlist:
        lines.append(f"- {item.symbol}: {item.reason} Risk: {item.risk_note}")
    lines.append("")
    return "\n".join(lines)

