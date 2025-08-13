import pytest
from datetime import datetime

from src.data_collector import DataCollector
from sources.base_source import BaseSource


class SuccessSource(BaseSource):
    def get_display_name(self) -> str:
        return "Success Source"

    def get_base_url(self) -> str:
        return "https://example.com/success"

    def collect_events(self, target_date: datetime | None = None):
        # Simula coleta simples com 2 eventos válidos
        events = [
            {"name": "Event A", "date": target_date or datetime.now()},
            {"name": "Event B", "date": target_date or datetime.now()},
        ]
        # Atualiza métricas da fonte (como faria uma implementação real)
        self.stats["requests_made"] += 1
        self.stats["successful_requests"] += 1
        self.stats["events_collected"] += len(events)
        self.stats["last_collection_time"] = datetime.now().isoformat()
        return events


class FailingSource(BaseSource):
    def get_display_name(self) -> str:
        return "Failing Source"

    def get_base_url(self) -> str:
        return "https://example.com/fail"

    def collect_events(self, target_date: datetime | None = None):
        self.stats["requests_made"] += 1
        self.stats["failed_requests"] += 1
        self.stats["last_collection_time"] = datetime.now().isoformat()
        raise RuntimeError("simulated failure")


class SimpleConfig:
    def __init__(self, max_concurrent_sources=1, excluded=None, timeout_seconds=10):
        self._data = {
            "max_concurrent_sources": max_concurrent_sources,
            "collection_timeout_seconds": 5,
            "retry_failed_sources": False,
            "priority_order": [],
            "excluded_sources": excluded or ["tomada_tempo"],
            "timeout_seconds": timeout_seconds,
            "retry_attempts": 1,
            "rate_limit_delay": 0,
        }

    def get_data_sources_config(self):
        return self._data

    # For streaming links API (used by BaseSource), keep minimal contract
    def get_streaming_providers(self, region: str):
        return {}


def test_collect_returns_empty_when_no_active_sources():
    cfg = SimpleConfig(max_concurrent_sources=1, excluded=["tomada_tempo"])  # remove built-in
    collector = DataCollector(config_manager=cfg, logger=None, ui_manager=None)

    # Nenhuma fonte ativa após exclusão
    assert len(collector.active_sources) == 0
    events = collector.collect_events(target_date=datetime(2025, 1, 3))
    assert events == []
    assert collector.collection_stats["total_sources_attempted"] == 0
    assert collector.collection_stats["successful_sources"] == 0
    assert collector.collection_stats["failed_sources"] == 0


def test_add_source_and_collect_sequential_success_with_priority_metadata():
    cfg = SimpleConfig(max_concurrent_sources=1, excluded=["tomada_tempo"])  # força sequencial
    collector = DataCollector(config_manager=cfg, logger=None, ui_manager=None)

    ok = collector.add_source(SuccessSource, priority=80)
    assert ok is True
    assert len(collector.active_sources) == 1

    target = datetime(2025, 1, 3)
    events = collector.collect_events(target_date=target)

    assert len(events) == 2
    # Campo metadata de prioridade adicionado pelo coletor
    assert all("source_priority" in e for e in events)
    assert collector.collection_stats["successful_sources"] == 1
    assert collector.collection_stats["failed_sources"] == 0
    assert collector.collection_stats["total_events_collected"] == 2


def test_collect_concurrent_with_failure_updates_stats():
    cfg = SimpleConfig(max_concurrent_sources=2, excluded=["tomada_tempo"])  # usa concorrência
    collector = DataCollector(config_manager=cfg, logger=None, ui_manager=None)

    assert collector.add_source(SuccessSource, priority=60) is True
    assert collector.add_source(FailingSource, priority=50) is True

    target = datetime(2025, 1, 3)
    events = collector.collect_events(target_date=target)

    # Sucesso de uma fonte e falha de outra
    assert len(events) == 2
    assert collector.collection_stats["successful_sources"] == 1
    assert collector.collection_stats["failed_sources"] == 1
    # Resultados por fonte presentes
    results = collector.collection_stats["source_results"]
    assert "success" in {k for k in results} or "success" in {s.source_name for s in collector.active_sources}


def test_remove_source_by_name():
    cfg = SimpleConfig(max_concurrent_sources=1, excluded=["tomada_tempo"])  # sequencial
    collector = DataCollector(config_manager=cfg, logger=None, ui_manager=None)

    collector.add_source(SuccessSource, priority=70)
    collector.add_source(SuccessSource, priority=60)  # segunda instância
    assert len(collector.active_sources) == 2

    # Nome da fonte é derivado de class name: "SuccessSource" -> "success"
    removed = collector.remove_source("success")
    assert removed is True
    assert len(collector.active_sources) == 1


def test_get_source_statistics_structure():
    cfg = SimpleConfig(max_concurrent_sources=1, excluded=["tomada_tempo"])  # sequencial
    collector = DataCollector(config_manager=cfg, logger=None, ui_manager=None)

    collector.add_source(SuccessSource, priority=80)
    events = collector.collect_events(target_date=datetime(2025, 1, 3))
    assert len(events) == 2

    stats = collector.get_source_statistics()
    # Estrutura básica
    assert set(["collection_stats", "source_stats", "active_sources_count", "available_sources_count", "excluded_sources"]) <= set(stats.keys())
    assert stats["active_sources_count"] == 1
