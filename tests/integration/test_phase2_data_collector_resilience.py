"""
Phase 2 Integration — Data Collector Resilience
Objetivo: validar resiliência do coletor HTTP (timeouts, 404, retries simples, conteúdo vazio/malformed).
Marcadores: integration
"""

import pytest

pytestmark = pytest.mark.integration


def test_placeholder_data_collector_resilience():
    pytest.skip("TODO: implementar cenários reais conforme plano da issue #105")
