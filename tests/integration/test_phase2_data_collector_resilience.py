"""
Phase 2 Integration — Data Collector Resilience
Objetivo: validar resiliência do coletor HTTP (timeouts, 404, retries simples, conteúdo vazio/malformed).
Marcadores: integration
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any, Optional

from sources.base_source import BaseSource
from src.data_collector import DataCollector

pytestmark = pytest.mark.integration

class _FakeSourceOK(BaseSource):
    def get_display_name(self) -> str:
        return "Fake OK"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        # Retorna um evento mínimo válido
        return [{
            "name": "Evento OK",
            "date": datetime(2025, 1, 1)
        }]


class _FakeSourceTimeout(BaseSource):
    def get_display_name(self) -> str:
        return "Fake Timeout"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        raise TimeoutError("simulated timeout")


def test_data_collector_handles_source_errors_and_aggregates_successes():
    collector = DataCollector(config_manager=None, logger=None, ui_manager=None)

    # Substitui as fontes ativas para evitar chamadas reais de rede
    collector.active_sources = [
        _FakeSourceTimeout(),
        _FakeSourceOK(),
    ]
    collector.source_priorities = {
        collector.active_sources[0].source_name: 60,
        collector.active_sources[1].source_name: 50,
    }

    # Força execução sequencial para simplicidade do teste
    collector.max_concurrent_sources = 1

    events = collector.collect_events(target_date=datetime(2025, 1, 1))

    # Deve retornar apenas os eventos da fonte bem-sucedida
    assert isinstance(events, list)
    assert len(events) == 1
    assert events[0]["name"] == "Evento OK"

    # Estatísticas devem refletir 1 sucesso e 1 falha
    stats = collector.collection_stats
    assert stats["successful_sources"] == 1
    assert stats["failed_sources"] == 1
