import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="Fase 4 — TomadaTempo: implementar fluxo E2E (source -> processamento -> ICS) e snapshot canônico")
def test_phase4_tomada_tempo_end_to_end_snapshot():
    """Fluxo E2E TomadaTempo -> EventProcessor -> ICalGenerator

    Objetivo:
    - Validar geração de ICS canônico com normalização estável (UID fixo; sem campos voláteis; LF) a partir de HTMLs TomadaTempo.
    - Cobrir cenários AM/PM, sem minutos, overnight e categorias desconhecidas.

    Observações:
    - Usar fixtures simples e mocks de HTTP (sem rede real), isolando FS/TZ/random.
    - Comparar com snapshot em tests/snapshots/phase4/.
    """
    pass
