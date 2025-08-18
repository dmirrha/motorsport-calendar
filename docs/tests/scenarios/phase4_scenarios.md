# Fase 4 — TomadaTempo (Integração)

Referências:
- Fonte: `sources/tomada_tempo.py`
- Pipeline: `src/event_processor.py`, `src/ical_generator.py`
- Issue: #105 — Aumentar a cobertura de testes integrados para >80%
- PR: #110 — Plano/execução da Fase 4
- Regras: `.windsurf/rules/tester.md`

## Objetivo
Validar o fluxo ponta a ponta da fonte TomadaTempo, incluindo resiliência a erros comuns e geração de ICS canônico com snapshots normalizados.

## Cenários Cobertos (planejados)
- E2E com HTMLs representativos (AM/PM, sem minutos, overnight, categorias desconhecidas).
- Resiliência a erros: HTTP 404/500/timeout, HTML malformado, dados faltantes.
- Normalização consistente de snapshots ICS (UID fixo; remoção de campos voláteis; `\n`).

## Fixtures HTML
- `tests/fixtures/html/tomada_tempo_weekend_minimal.html` — baseline simples (estrutura canônica com `h5` + `p` + `ul/li`).
- `tests/fixtures/html/tomada_tempo_weekend_alt_header.html` — variação de cabeçalho (ex.: `PROGRAMAÇÃO`).
- `tests/fixtures/html/tomada_tempo_weekend_no_minutes.html` — horários sem minutos (ex.: `14 horas`, `às 8h`, `21`).
- `tests/fixtures/html/tomada_tempo_weekend_overnight.html` — sessões cruzando a meia-noite (dia D→D+1).
- `tests/fixtures/html/tomada_tempo_weekend_edge_cases.html` — AM/PM e categorias desconhecidas (ex.: `TEST SERIES`, `XYZ`).
- `tests/fixtures/html/tomada_tempo_weekend_malformed.html` — HTML propositalmente malformado (tags não fechadas/ordem incorreta).

## Execução e Estabilidade (a preencher após implementação)
Comandos base (sem gates globais para medir tempo cru):

```bash
pytest -o addopts="" tests/integration/test_phase4_tomada_tempo_end_to_end_snapshot.py -m integration --durations=0
pytest -o addopts="" tests/integration/test_phase4_tomada_tempo_errors.py -m integration --durations=0
```

Resultados (3 execuções consecutivas):
- Run 1: ... — .../...
- Run 2: ... — .../...
- Run 3: ... — .../...

Observações:
- Meta: zero flakes; tempo total < 30s local.

## Rastreabilidade
- Relacionado à meta de cobertura de integração da Issue #105 (Fase 4 — TomadaTempo).
- Evidências serão adicionadas em `CHANGELOG.md` (Unreleased) e `RELEASES.md` (Não Lançado) conforme progresso.
