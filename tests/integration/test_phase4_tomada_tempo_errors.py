import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="Fase 4 — TomadaTempo: implementar casos de erro (404/500/timeout, HTML inválido, dados faltantes) com mocks simples")
def test_phase4_tomada_tempo_errors():
    """Resiliência da fonte TomadaTempo sob condições adversas.

    Coberturas:
    - HTTP 404/500/timeout (sem rede real; usar patches de requests/session).
    - HTML malformado e dados faltantes.
    - Garantir falha controlada, sem crash, com estatísticas/metadados consistentes.
    """
    pass
