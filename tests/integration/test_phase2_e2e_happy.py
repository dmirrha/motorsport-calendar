import time
from datetime import datetime as _dt

import pytest

from src.data_collector import DataCollector
from src.event_processor import EventProcessor
from src.ical_generator import ICalGenerator
from tests.utils.ical_snapshots import compare_or_write_snapshot


def test_phase2_e2e_happy(freeze_datetime, fixed_uuid, patch_requests_session, dummy_response, tmp_path):
    """
    E2E caminho feliz: coleta TomadaTempo -> processa -> gera/valida ICS -> snapshot estável.

    Requisitos atendidos:
    - Mocks determinísticos para rede, datetime e UUID.
    - Estrutura mínima esperada pelo parser de "PROGRAMAÇÃO" do TomadaTempo.
    - Normalização e comparação de snapshot de ICS.
    - Execução < 30s.
    """
    # 1) Determinismo de tempo e UUID
    freeze_datetime(dt=_dt(2025, 8, 1, 12, 0, 0))  # Sexta-feira 01/08/2025
    fixed_uuid()

    # 2) HTMLs mínimos para o caminho feliz
    base_url = "https://www.tomadadetempo.com.br"
    programming_path = "/programacao-01-08-2025.html"
    programming_url = f"{base_url}{programming_path}"

    index_html = f"""
    <html>
      <body>
        <a href="{programming_path}">PROGRAMAÇÃO DA TV E INTERNET – 01/08/2025</a>
      </body>
    </html>
    """.strip()

    programming_html = """
    <html>
      <body>
        <h5>PROGRAMAÇÃO</h5>
        <p>SEXTA-FEIRA – 01/08/2025</p>
        <ul>
          <li>
            08:00 – FÓRMULA 1 – TREINO LIVRE 1 – Hungaroring –
            <a href="https://f1tv.com">F1 TV</a>
          </li>
          <li>
            10:30 – NASCAR CUP – Treino – Daytona –
            <a href="https://youtube.com/@nascar">YouTube</a>
          </li>
        </ul>
      </body>
    </html>
    """.strip()

    # 3) Router de respostas no Session.request
    def responder(url, **kwargs):
        if url.rstrip('/') == base_url:
            return dummy_response(text=index_html, url=url)
        if url == programming_url:
            return dummy_response(text=programming_html, url=url)
        # fallback
        return dummy_response(text="<html></html>", url=url, status_code=404)

    patch_requests_session(response_or_callable=responder)

    # 4) Executa pipeline E2E
    t0 = time.monotonic()

    collector = DataCollector()
    raw_events = collector.collect_events()  # usa _get_next_weekend() com freeze

    processor = EventProcessor()
    processed_events = processor.process_events(raw_events)

    ical = ICalGenerator()
    output_filename = "phase2_e2e_happy.ics"
    ics_path = ical.generate_calendar(processed_events, output_filename=output_filename)

    # 5) Validação básica do ICS
    validation = ical.validate_calendar(ics_path)
    assert validation.get("valid") is True, f"ICS inválido: {validation}"
    assert validation.get("events_count", 0) >= 1, "ICS sem eventos"

    # 6) Snapshot normalizado
    compare_or_write_snapshot(
        generated_path=ics_path,
        snapshot_path="tests/snapshots/phase2/phase2_e2e_happy.ics",
    )

    # 7) Performance
    dt = time.monotonic() - t0
    assert dt < 30.0, f"Teste E2E demorou {dt:.2f}s (esperado < 30s)"
