from datetime import date

from asharelab.data import MockAshareSource
from asharelab.memory import MarketMemory


def test_memory_roundtrip(tmp_path):
    memory = MarketMemory(tmp_path / "memory.sqlite")
    events = MockAshareSource().load_events(date(2026, 6, 15))
    memory.add_events(events)

    loaded = memory.recent_events()

    assert len(loaded) == len(events)
    assert "低空经济" in memory.topic_counts()

