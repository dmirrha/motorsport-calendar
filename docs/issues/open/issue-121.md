# Issue #121 — TomadaTempo IT2 — Cobertura de Integração ≥ 80%

- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/121
- Estado: open
- Criada em: 2025-08-18T19:47:09-03:00

## 🧭 Objetivo
Alcançar cobertura de testes de integração ≥ 80% com foco na fonte `TomadaTempo` (IT2), garantindo robustez do parser/coletor/processador e consistência do ICS final.

## 🔎 Escopo
- Expandir cenários além do IT1 (happy/missing/malformed) para casos avançados e realistas.
- Validar impacto no pipeline completo até o ICS.

## 🛠️ Plano Técnico

### Cenários Alvo (TomadaTempo)
- Datas e Timezones
  - DST/bordas; conversões corretas; normalização e ordenação por DTSTART.
- Multi-day / Overnight
  - Eventos que cruzam meia-noite; início/fim coerentes; snapshot ICS estável.
- Entities/Encoding
  - HTML entities (&amp;, &nbsp;, &mdash;, etc.), acentos/UTF-8, normalização de whitespace.
- Duplicatas
  - Dedupe por título+data+local; priorizar registro mais completo; idempotência.
- Streaming > 3
  - Páginas/itens adicionais; garantir coleta parcial estável (sem loop infinito).
- Locais ausentes/ambíguos
  - Campos opcionais; placeholders claros; aviso sem travar o pipeline.

### Fixtures a criar (em `tests/fixtures/html/tomada_tempo/`)
- `programming_entities.html`
- `programming_multiday.html`
- `programming_timezone_dst.html`
- `programming_duplicates.html`
- `programming_streaming_overflow.html`
- `programming_missing_location.html`

### Testes de Integração a implementar (em `tests/integration/`)
- `test_it2_tomada_tempo_dates_tz.py`
  - Asserts de parsing de datas/TZ; ordenação; consistência no payload e ICS.
- `test_it2_tomada_tempo_entities_and_duplicates.py`
  - Normalização de strings; dedupe; preservação do mais completo; estabilidade do ICS.
- `test_it2_tomada_tempo_streaming_constraints.py`
  - Limites de paginação/itens; coleta parcial; nenhum crash; warnings controlados.
- `test_it2_tomada_tempo_multiday_and_location.py`
  - Overnight/multi-day; locais ausentes → placeholders; ICS determinístico.

### Execução e Métricas
- `pytest -q -m integration --cov=src --cov=sources --cov-report=xml:coverage_integration.xml`
- Meta: ≥80% integração, 0 flakes (2–3 execuções locais), <30s no CI.
- Acompanhar Codecov (flags/components) e relatórios do workflow `Tests`.

## ✅ Critérios de Aceite
- Cobertura de integração ≥80% com estabilidade.
- ICS consistente (snapshots normalizados) para os novos cenários.
- Logs/warnings apenas quando agregam valor; sem ruído/erros silenciosos.
- Documentação sincronizada (CHANGELOG [Unreleased], RELEASES, `docs/tests/overview.md`).

## ⚠️ Riscos e Mitigações
- Anti-flakes: fixtures determinísticas, tolerâncias de horário mínimas, mocks simples quando necessário.
- Performance: parsing direcionado e reuso de fixtures; evitar sleeps desnecessários.

## 📚 Governança e Documentação
- Atualizar: `CHANGELOG.md`, `RELEASES.md`, `docs/tests/overview.md`.
- Rastreabilidade: referenciar esta issue em PRs e commits (SemVer 0.x.y).

## 🌿 Branch e PR
- Branch: `chore/it2-tomadatempo-coverage-80`.
- PR: descritivo, com checklist e links para artefatos (coverage/Codecov, HTML fixtures).

## 📋 Checklist de Execução
- [ ] Planejar e detalhar cenários (datas/TZ, multi-day, entities, duplicatas, streaming>3, locais ausentes)
- [ ] Criar fixtures HTML em `tests/fixtures/html/tomada_tempo/`
- [ ] Implementar testes: `dates_tz`
- [ ] Implementar testes: `entities_and_duplicates`
- [ ] Implementar testes: `streaming_constraints`
- [ ] Implementar testes: `multiday_and_location`
- [ ] Rodar `pytest -m integration` 3× local, validar estabilidade e ≥80%
- [ ] Atualizar documentação (CHANGELOG, RELEASES, docs/tests/overview.md)
- [ ] Abrir PR e referenciar esta issue
