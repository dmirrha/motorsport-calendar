"""
Phase 3 — Iteração 1: Testes de integração (concorrência) para DataCollector
Objetivo: validar agregação parcial com execução concorrente e tratamento de erros sem crash.
Marcadores: integration
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import pytest

from sources.base_source import BaseSource
from src.data_collector import DataCollector


pytestmark = pytest.mark.integration


class _FakeSourceFastOK(BaseSource):
    def get_display_name(self) -> str:
        return "Fake Fast OK"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        # pequeno delay para garantir execução em thread separada sem flake
        time.sleep(0.05)
        return [{
            "name": "Evento OK Conc",
            "date": datetime(2025, 1, 1)
        }]


class _FakeSourceError(BaseSource):
    def get_display_name(self) -> str:
        return "Fake Error"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        raise RuntimeError("simulated failure")


def test_data_collector_concurrent_aggregates_and_handles_errors():
    collector = DataCollector(config_manager=None, logger=None, ui_manager=None)

    # Força duas fontes e concorrência > 1
    ok_source = _FakeSourceFastOK()
    err_source = _FakeSourceError()
    collector.active_sources = [err_source, ok_source]
    collector.source_priorities = {
        err_source.source_name: 60,
        ok_source.source_name: 50,
    }
    collector.max_concurrent_sources = 2
    collector.collection_timeout = 5

    events = collector.collect_events(target_date=datetime(2025, 1, 1))

    # Apenas eventos da fonte bem-sucedida devem ser retornados
    assert isinstance(events, list)
    assert len(events) == 1
    assert events[0]["name"] == "Evento OK Conc"
    # Metadata de prioridade adicionada no caminho do coletor
    assert "source_priority" in events[0]

    # Estatísticas devem refletir 1 sucesso e 1 falha
    stats = collector.collection_stats
    assert stats["successful_sources"] == 1
    assert stats["failed_sources"] == 1

    # Estatísticas detalhadas por fonte disponíveis via get_source_statistics
    detail = collector.get_source_statistics()
    assert detail["collection_stats"]["total_events_collected"] == 1
    assert detail["active_sources_count"] == 2
    assert len(detail["source_stats"]) == 2
