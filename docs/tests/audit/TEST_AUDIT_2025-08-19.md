# Relatório de Auditoria da Suíte de Testes

Data: 2025-08-19
Escopo: Projeto “Race Calendar” — auditoria de qualidade dos testes automatizados (unit e integração)

## Sumário de Pontuações (0–10)

- Arquitetura de testes: 8.5
- Qualidade dos casos de teste: 7.5
- Cobertura real vs. métricas: 7.0
- Manutenibilidade: 8.0
- Integração CI/CD: 8.5
- Segurança/Conformidade: 8.0

## Evidências-Chave

- Arquitetura e governança
  - Estrutura clara: `tests/unit/`, `tests/integration/`, `tests/regression/`, `tests/policy/`, `tests/snapshots/` (raiz `tests/`).
  - Markers registrados em `pytest.ini` e policiados por teste de política: `tests/policy/test_markers_policy.py`.
  - Guia do test harness documentado: `tests/README.md`.
  - Fixtures determinísticas: TZ fixa, seed de random, freeze de datetime, UUID fixo, patches de rede em `tests/conftest.py`.

- Casos representativos e boas práticas
  - Integração com snapshot ICS e normalização: `tests/integration/test_phase2_*` + `tests/utils/ical_snapshots.py`.
  - Resiliência de coleta com retries (transiente vs permanente): `tests/unit/data_collector/test_data_collector_retry.py`.
  - XFail explícitos para funcionalidades pendentes:
    - Ordenação ICS: `tests/integration/test_phase2_dedupe_order_consistency.py` (xfail no bloco final — linhas 79–82).
    - Deduplicação TomadaTempo ainda em evolução: `tests/integration/test_it2_tomada_tempo_entities_and_duplicates.py`.

- Cobertura e métricas
  - Branch coverage habilitado em `.coveragerc` (com omit para testes e `__init__.py`).
  - Histórico de cobertura incremental no `tests/README.md` (ex.: 61.52% global em fase recente).
  - Codecov com flags por job e components mapeados: `codecov.yml`.

- CI/CD
  - Workflow segmentado e com artefatos: `.github/workflows/tests.yml`.
  - Uploads de cobertura separados (unit/integration/e2e), JUnit, e Test Analytics do Codecov habilitado.

- Estabilidade
  - Não há `flaky`, `rerunfailures` ou `pytest.mark.slow/timeout` nos testes (buscas limpas).
  - README sugere rodar suíte 3x local sem flakes; integração E2E “happy” com tempos estáveis (~2s).

## Pontos Fortes

- [governança] Políticas de markers impedem regressões de classificação de testes (`tests/policy/test_markers_policy.py`).
- [determinismo] Conjunto robusto de fixtures para TZ, tempo, UUID, rede controlada (`tests/conftest.py`).
- [observabilidade] Snapshots ICS com normalização e validação (`tests/utils/ical_snapshots.py`).
- [CI robusto] Pipeline com separação por tipo, artefatos, Codecov por flags e componentes (`tests.yml`, `codecov.yml`).
- [doc tests] `tests/README.md` detalhado, com exemplos de execução, métricas e referências.

## Lacunas e Riscos

- [xfail pendentes] Ordenação no ICS e deduplicação (podem mascarar regressões se não forem endereçados).
- [ausência de property testing] Sem `hypothesis` para invariantes (parsers de datas, normalização, dedupe, ordenação ICS).
- [ausência de mutation testing] Sem `mutmut`/`cosmic-ray`; risco de cobertura “otimista”.
- [tempo/timeout] Integração valida “<30s” via assert, mas não há `pytest-timeout` para evitar hangs.
- [flakiness guard] Sem job dedicado de detecção de flakes (execuções repetidas/ordem aleatória) no CI.
- [gates de cobertura] Gate global baixo (45% conforme `tests/README.md`) e Codecov informativo (não bloqueia PRs); falta de “patch gate”.
- [segurança de logs] Oportunidade de testes assegurando redaction de tokens/segredos em logs/payloads.

## Recomendações Prioritárias (Plano P0–P2)

### P0 (curto prazo / alto impacto)
- Resolver xfails:
  - Ordenação ICS: ordenar antes da escrita (no `ICalGenerator` ou pipeline) e converter `xfail` em `pass` em `tests/integration/test_phase2_dedupe_order_consistency.py`.
  - Deduplicação TomadaTempo: ajustar regra/fuzzy threshold e ativar teste `tests/integration/test_it2_tomada_tempo_entities_and_duplicates.py`.
- Introduzir `pytest-timeout` e timeouts por escopo:
  - Global curto p/ unit (5–10s) e maior p/ integração (60–120s).
- Ativar `pytest-randomly` para embaralhar ordem e expor dependências entre testes.

### P1 (médio prazo)
- Property-based testing com `hypothesis`:
  - Invariantes de parsing de datas/horas/timezones (round-trips e equivalências).
  - Invariantes de dedupe (idempotência, comutatividade parcial, estabilidade de escolha por prioridade).
  - Ordenação ICS (ordem estável sob empates).
- Mutation testing (baseline semanal/noturna):
  - `mutmut` em módulos críticos: `src/event_processor.py`, `src/ical_generator.py`, `sources/base_source.py`.
- Cobertura:
  - Introduzir “patch coverage gate” via Codecov (patch ≥ 85%) e elevar gate global gradualmente (+5pp por release até 75–80%).
- Flake detection no CI:
  - Job noturno executando a suíte 3x com `pytest-repeat` e coleta de timings, analisando Test Analytics do Codecov.

### P2 (longo prazo)
- Testes de segurança/privacidade:
  - Redaction de segredos/tokens em logs e dumps de erro; fixtures/validadores dedicados.
- Performance budgets:
  - Medir tempos por módulo e falhar se exceder (histórico via JUnit timings).
- Ampliar E2E:
  - Além do “happy path”, cobrir erros de rede, dados malformados, recuperações.
- Documentação e governança:
  - Registrar padrões de invariantes, mutation/property testing e metas de cobertura em `tests/README.md` e `REQUIREMENTS.md`.

## Quick Wins

- Adicionar `pytest-timeout` e `pytest-randomly` no `requirements-dev.txt` e configurar no `pytest.ini`.
- Converter xfail de ordenação após ordenar eventos no ICS.
- Habilitar “patch coverage gate” informativo no Codecov e promover a “required” depois de 1–2 ciclos.

## Itens Sugeridos para Issues

- feat(test): garantir ordenação ICS e remover xfail
  - Ref: `tests/integration/test_phase2_dedupe_order_consistency.py`.
- feat(test): invariantes com hypothesis para parsers e dedupe
  - Alvos: `src/event_processor.py`, `src/ical_generator.py`, `sources/base_source.py`.
- chore(ci): adicionar pytest-timeout e pytest-randomly
  - Configuração e thresholds diferenciados unit/integration.
- chore(ci): habilitar patch coverage gate e job de flakiness nightly
  - Codecov patch ≥ 85%, repetir suíte x3 com timings.

## Observações de Conformidade

- OIDC no Codecov reduz risco de segredos; manter.
- Ao adotar as recomendações, atualizar documentação: `CHANGELOG.md`, `CONTRIBUTING.md`, `PROJECT_STRUCTURE.md`, `README.md`, `RELEASES.md`, `REQUIREMENTS.md`, `CONFIGURATION_GUIDE.md` e docs sob `docs/`.

## Próximos Passos

- Aprovação do plano P0 para iniciar correções e hardening da suíte.
- Opcional: preparar diffs para `pytest.ini`/`requirements-dev.txt` (timeout/randomly) e um patch no `ICalGenerator` para ordenação estável.
