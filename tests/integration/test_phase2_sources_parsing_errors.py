"""
Phase 2 Integration — Sources Parsing Errors
Objetivo: validar resiliência a erros de parsing nas fontes (malformed HTML/JSON/ICS, campos ausentes, tipos inválidos).
Marcadores: integration
"""

import pytest
from datetime import datetime
from sources.tomada_tempo import TomadaTempoSource

pytestmark = pytest.mark.integration

def test_parse_text_content_basic_line_extracts_event_fields():
    # HTML simples contendo linha textual com palavras-chave de motorsport
    html = """
    <html><body>
      <div>Outros conteúdos irrelevantes</div>
      <p>F1 GP do Brasil - 20/10/2025 14:00 - Interlagos</p>
    </body></html>
    """

    src = TomadaTempoSource()
    target_date = datetime(2025, 10, 20)

    events = src._parse_text_content(html, target_date)

    assert isinstance(events, list) and len(events) >= 1
    evt = events[0]

    # Campos essenciais devem estar presentes (nome e data pelo menos)
    assert evt.get("name")
    assert evt.get("date") is not None
    # Quando possível, tempo e localização devem ser detectados
    assert evt.get("time") is not None
    assert evt.get("location")


def test_parse_text_content_uses_programming_context_when_date_missing():
    # Linha sem data explícita, deve associar à data do contexto de programação
    html = """
    <html><body>
      <p>MotoGP - Sprint 16:00</p>
    </body></html>
    """

    src = TomadaTempoSource()
    target_date = datetime(2025, 10, 20)
    programming_context = {
        "weekend_dates": [datetime(2025, 10, 20)]
    }

    events = src._parse_text_content(html, target_date, programming_context=programming_context)

    assert len(events) >= 1
    evt = events[0]

    # Deve preencher a data a partir do contexto quando ausente na linha
    assert evt.get("date") == programming_context["weekend_dates"][0]
    # Campo auxiliar indica que a data veio do contexto
    assert evt.get("from_context") is True
