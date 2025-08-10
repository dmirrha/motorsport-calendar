# Issue #48 — Fase 1: Mocks essenciais

Referências:
- Epic: #45 — Automação de testes
- Milestone: #2 — Automação de testes - Fase 1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/48

## Objetivo
Garantir determinismo e isolamento em testes unitários por meio de mocks básicos de tempo, aleatoriedade, rede, sistema de arquivos e variáveis de ambiente.

## Plano de Execução
1. Mock de tempo TZ-aware e aleatoriedade
   - Fixture para data/hora fixa (TZ `America/Sao_Paulo`) via `monkeypatch` de `datetime`/`time`
   - Fixture para `random.seed(0)` com restauração
2. Mock de rede
   - Evitar chamadas externas em unit tests
   - Usar `monkeypatch`/stubs em `requests.get`/`requests.post`
3. Isolamento de filesystem
   - Utilizar `tmp_path`/`tmp_path_factory` para arquivos temporários
   - Redirecionar quaisquer paths de escrita/leitura nos testes
4. Variáveis de ambiente
   - Fixture para `monkeypatch.setenv`/`delenv`
5. Documentação e exemplos
   - Atualizar `tests/README.md` com convenções de mocks
   - Adicionar exemplos mínimos em testes existentes
6. Validação
   - Executar `pytest --maxfail=1 -q` e garantir resultados estáveis

## PARE — Autorização
- Submeter PR de rascunho do plano para aprovação antes de alterar testes existentes.

## Progresso
- [x] Branch criada: `chore/tests-mocks-essenciais-48-20250810`
- [x] PR de rascunho aberto com este plano (referenciando #48 e épico #45)
- [x] Fixtures de tempo e random criadas
- [x] Mocks de rede definidos
- [x] Isolamento de FS aplicado com `tmp_path`
- [x] Fixtures de env aplicadas
- [x] `tests/README.md` atualizado (seção de mocks)
 - [x] Validação: `45 passed`; cobertura total: 28.75%
 - [x] Documentação atualizada com mocks essenciais e gate 25%: `CHANGELOG.md` (Não Lançado), `RELEASES.md` (Próximo), `README.md` (🧪 Testes), `tests/README.md`. Gate configurado em `pytest.ini` (`--cov-fail-under=25`).
 - [x] Plano sincronizado: `docs/TEST_AUTOMATION_PLAN.md` com validação “45 passed; 28.75%” (2025-08-10)
 - [x] PR #55 atualizada: resumo com suíte estável, gate 25%, documentos sincronizados e checklists alinhados

## Checklist — Mocks essenciais
- [x] Definir padrões de patch (compatíveis com shims):
  - [x] `sources.tomada_tempo.requests.get`
  - [x] `sources.base_source.requests.Session`
- [x] Tempo e aleatoriedade: fixture TZ-aware (America/Sao_Paulo) e `random.seed(0)` com restauração
- [x] Isolamento de filesystem: uso de `tmp_path`/`tmp_path_factory` — ver `tests/unit/utils/test_payload_manager.py`
- [x] Variáveis de ambiente: `monkeypatch.setenv`/`delenv` — ver `tests/unit/test_env_vars.py`
- [x] Simular cenários: sucesso, timeout, HTTPError, HTML malformado — ver `tests/unit/sources/base_source/test_make_request.py` e `tests/unit/sources/tomada_tempo/test_parse_calendar_page.py`

## Critérios de Aceite
- Testes não dependem de rede/tempo/FS real
- Execução repetível e estável
- Convenções documentadas em `tests/README.md`
