import pytest
from datetime import datetime

from src.data_collector import DataCollector
from sources.base_source import BaseSource


class FlakyTransientSource(BaseSource):
    """
    Falha com TimeoutError na primeira chamada e tem sucesso na segunda.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._calls = 0

    def get_display_name(self) -> str:
        return "Flaky Transient Source"

    def get_base_url(self) -> str:
        return "https://example.com/flaky"

    def collect_events(self, target_date: datetime | None = None):
        self._calls += 1
        # contabiliza tentativa
        self.stats["requests_made"] += 1
        self.stats["last_collection_time"] = datetime.now().isoformat()

        if self._calls == 1:
            # falha transitória
            self.stats["failed_requests"] += 1
            raise TimeoutError("simulated transient timeout")

        # sucesso na 2ª chamada
        events = [
            {"name": "Event A", "date": target_date or datetime.now()},
            {"name": "Event B", "date": target_date or datetime.now()},
        ]
        self.stats["successful_requests"] += 1
        self.stats["events_collected"] += len(events)
        return events


class AlwaysTimeoutSource(BaseSource):
    """
    Sempre lança TimeoutError (transitório), para esgotar os retries.
    """
    def get_display_name(self) -> str:
        return "Always Timeout Source"

    def get_base_url(self) -> str:
        return "https://example.com/timeout"

    def collect_events(self, target_date: datetime | None = None):
        self.stats["requests_made"] += 1
        self.stats["failed_requests"] += 1
        self.stats["last_collection_time"] = datetime.now().isoformat()
        raise TimeoutError("permanent timeout for test")


class SimpleConfig:
    def __init__(
        self,
        max_concurrent_sources=1,
        excluded=None,
        timeout_seconds=10,
        retry_failed_sources=True,
        max_retries=1,
        retry_backoff_seconds=0.0,
    ):
        self._data = {
            "max_concurrent_sources": max_concurrent_sources,
            "collection_timeout_seconds": 5,
            "retry_failed_sources": retry_failed_sources,
            "priority_order": [],
            "excluded_sources": excluded or ["tomada_tempo"],
            "timeout_seconds": timeout_seconds,
            # mantemos retry_attempts por compatibilidade (não usado diretamente aqui)
            "retry_attempts": 1,
            "rate_limit_delay": 0,
            # novas chaves
            "max_retries": max_retries,
            "retry_backoff_seconds": retry_backoff_seconds,
        }

    def get_data_sources_config(self):
        return self._data

    # For streaming links API (used by BaseSource), keep minimal contract
    def get_streaming_providers(self, region: str):
        return {}


def test_retry_succeeds_after_transient_timeout():
    cfg = SimpleConfig(
        max_concurrent_sources=1,  # força sequencial
        excluded=["tomada_tempo"],
        retry_failed_sources=True,
        max_retries=1,  # 1 retry adicional além da primeira
        retry_backoff_seconds=0.0,  # determinístico e rápido
    )
    collector = DataCollector(config_manager=cfg, logger=None, ui_manager=None)

    assert collector.add_source(FlakyTransientSource, priority=80) is True

    target = datetime(2025, 1, 3)
    events = collector.collect_events(target_date=target)

    assert len(events) == 2
    assert collector.collection_stats["successful_sources"] == 1
    assert collector.collection_stats["failed_sources"] == 0

    # Resultados por fonte com sucesso
    results = collector.collection_stats["source_results"]
    assert "flakytransient" in results
    assert results["flakytransient"]["success"] is True
    assert results["flakytransient"]["events_count"] == 2


def test_retry_exhausts_and_fails():
    cfg = SimpleConfig(
        max_concurrent_sources=1,
        excluded=["tomada_tempo"],
        retry_failed_sources=True,
        max_retries=2,  # 2 tentativas adicionais
        retry_backoff_seconds=0.0,
    )
    collector = DataCollector(config_manager=cfg, logger=None, ui_manager=None)

    assert collector.add_source(AlwaysTimeoutSource, priority=80) is True

    target = datetime(2025, 1, 3)
    events = collector.collect_events(target_date=target)

    # Nenhum evento coletado, fonte falhou após esgotar tentativas
    assert len(events) == 0
    assert collector.collection_stats["successful_sources"] == 0
    assert collector.collection_stats["failed_sources"] == 1

    results = collector.collection_stats["source_results"]
    assert "alwaystimeout" in results
    assert results["alwaystimeout"]["success"] is False
    assert "timed out" in results["alwaystimeout"]["error"].lower() or "timeout" in results["alwaystimeout"]["error"].lower()
