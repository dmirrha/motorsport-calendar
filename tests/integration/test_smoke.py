import pytest


@pytest.mark.integration
def test_smoke_integration_marker_and_env():
    """Teste de fumaça mínimo para o ambiente de testes de integração.
    Critérios: execução rápida e determinística.
    """
    assert True
