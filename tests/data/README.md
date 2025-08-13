# tests/data

Este diretório armazena artefatos mínimos para testes (HTML/JSON simulados, payloads e fixtures).

Recomendações:
- Use arquivos pequenos e determinísticos.
- Nomeie por domínio de teste (ex.: `tomada_tempo_calendar_sample.html`).
- Carregue o conteúdo com `Path(__file__).resolve().parent / "..."` nos próprios testes.

Observação: Há shims para HTTP em `tests/conftest.py` (`dummy_response`, `patch_requests_get`, `patch_requests_session`).
Você pode combinar dados deste diretório com essas fixtures para simular respostas de rede sem acesso externo.
