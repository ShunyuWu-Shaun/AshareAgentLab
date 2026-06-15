from datetime import date

from asharelab.agents import AgentCommittee
from asharelab.data import MockAshareSource


def test_committee_generates_hypotheses_and_watchlist():
    events = MockAshareSource().load_events(date(2026, 6, 15))
    brief = AgentCommittee().run(events, date(2026, 6, 15))

    assert brief.hypotheses
    assert brief.watchlist
    assert len(brief.reports) == 4

