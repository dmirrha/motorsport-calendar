from datetime import datetime, timedelta
from typing import List

import pytest
import pytz
from hypothesis import given, strategies as st

from src.event_processor import EventProcessor


def _tz():
    return pytz.timezone("America/Sao_Paulo")


def _make_event(name: str, dt: datetime, category: str, location: str, prio: int, links: List[str], eid: str) -> dict:
    return {
        "event_id": eid,
        "name": name,
        "display_name": name.title(),
        "datetime": dt,
        "detected_category": category,
        "location": location,
        "source_priority": prio,
        "streaming_links": links,
        "official_url": "",
    }


def _similar_variants(base: dict, i: int, time_tol_min: int = 20) -> dict:
    dt = base["datetime"] + timedelta(minutes=i % (time_tol_min // 2 + 1))
    # pequenas variações no nome preservam alta similaridade
    name = base["name"].replace(" ", "  ") if i % 2 == 0 else base["name"].upper()
    links = list(set(base["streaming_links"] + [f"http://s{i}.example.com"]))
    prio = base["source_priority"] + (i % 2)
    return _make_event(name, dt, base["detected_category"], base["location"], prio, links, f"{base['event_id']}-{i}")


@pytest.mark.property
@given(
    n_groups=st.integers(min_value=1, max_value=3),
    group_sizes=st.lists(st.integers(min_value=1, max_value=4), min_size=1, max_size=3),
    base_hour=st.integers(min_value=8, max_value=18),
)
def test_dedup_idempotent_and_merges_links(n_groups, group_sizes, base_hour):
    tz = _tz()
    ep = EventProcessor(config_manager=None, logger=None, ui_manager=None)

    # constrói grupos totalmente similares (transitividade): mesmo nome base, categoria e localização
    events: List[dict] = []
    day = 15
    for g in range(n_groups):
        base_dt = tz.localize(datetime(2024, 5, min(25, day + g), base_hour, 0))
        base = _make_event(
            name=f"formula 1 gp {g}",
            dt=base_dt,
            category="formula 1",
            location="interlagos",
            prio=50,
            links=["http://a.example.com"],
            eid=f"eid-{g}"
        )
        size = group_sizes[g % len(group_sizes)]
        group = [base] + [_similar_variants(base, i + 1) for i in range(max(0, size - 1))]
        events.extend(group)

    # propriedade 1: idempotência
    once = ep._deduplicate_events(events)
    twice = ep._deduplicate_events(once)
    assert once == twice

    # propriedade 2: merge de links resulta em conjunto (sem duplicatas) e é estável
    for ev in once:
        assert len(ev.get("streaming_links", [])) == len(set(ev.get("streaming_links", [])))

    again = ep._deduplicate_events(list(reversed(events)))
    # como grupos são totalmente similares, resultado deve ser estável sob permutação
    # comparamos por tupla determinística (name normalizado pode variar por maiúsculas, então usamos lower())
    key = lambda e: (e["name"].lower(), e["detected_category"], e.get("location", ""))
    assert sorted(map(key, once)) == sorted(map(key, again))
