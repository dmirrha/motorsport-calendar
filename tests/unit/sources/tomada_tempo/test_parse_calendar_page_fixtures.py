import pytest
from pathlib import Path

from sources.tomada_tempo import TomadaTempoSource


class _LoggerStub:
    def __init__(self):
        self.debugs = []

    def debug(self, msg):
        self.debugs.append(msg)


@pytest.mark.unit
@pytest.mark.parametrize(
    "fixture_name, min_events, expect_unknown_min",
    [
        ("tomada_tempo_weekend_minimal.html", 3, None),
        ("tomada_tempo_weekend_alt_header.html", 3, None),
        ("tomada_tempo_weekend_edge_cases.html", 3, 1),
        ("tomada_tempo_weekend_no_minutes.html", 3, None),
        ("tomada_tempo_weekend_overnight.html", 3, None),
    ],
)
def test_parse_calendar_page_with_fixtures(fixture_name, min_events, expect_unknown_min):
    fixture_path = (
        Path(__file__).parents[4]
        / "tests"
        / "fixtures"
        / "html"
        / fixture_name
    )
    assert fixture_path.is_file(), f"Fixture não encontrado: {fixture_path}"

    html = fixture_path.read_text(encoding="utf-8")

    src = TomadaTempoSource(config_manager=None, logger=_LoggerStub())
    # target_date é irrelevante para _parse_calendar_page (datas vêm do HTML)
    events = src._parse_calendar_page(html_content=html, target_date=__import__("datetime").datetime.now())

    assert isinstance(events, list)
    assert len(events) >= min_events

    # Valida campos principais do primeiro evento extraído
    e0 = events[0]
    assert isinstance(e0, dict)
    assert e0.get("name")
    assert e0.get("date")  # formato 'YYYY-MM-DD' conforme _parse_event_from_li
    # time pode ser None em alguns casos, mas em nossos fixtures possui hora
    assert "time" in e0
    assert e0.get("category")
    assert "streaming_links" in e0

    # Edge: validar que o fixture de edge cases produz ao menos um 'Unknown'
    if expect_unknown_min:
        unknown_count = sum(1 for ev in events if ev.get("category") == "Unknown")
        assert unknown_count >= expect_unknown_min
