"""
Phase 2 Integration — Sources Parsing Errors
Objetivo: validar resiliência a erros de parsing nas fontes (malformed HTML/JSON/ICS, campos ausentes, tipos inválidos).
Marcadores: integration
"""

import pytest

pytestmark = pytest.mark.integration


def test_placeholder_parsing_errors():
    pytest.skip("TODO: implementar cenários reais conforme plano da issue #105")
