# Issue 160 — F1b: Deduplicação semântica (threshold 0.85)

- ID: 3356426557
- Número: 160
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/160
- Criado em: 2025-08-26T16:56:29Z
- Atualizado em: 2025-08-26T17:09:12Z
- Labels: enhancement, needs-triage, priority: P1, ai, dedup

## Contexto
Adicionar camada de similaridade semântica à deduplicação em `src/event_processor.py::_are_events_similar()`, mantendo fuzzy/heurísticas existentes e o determinismo de `_select_best_event()`. Utiliza o `EmbeddingsService` (issue #165) local/offline.

- Threshold alvo: `0.85`, configurável via `ai.thresholds.dedup`.
- Opt-in via `ai.enabled=true`.

## Objetivo
- Melhorar recall/precisão da deduplicação combinando score heurístico (fuzzy) com similaridade semântica (cosine) de nomes e locais.
- Preservar determinismo do `_select_best_event()` em empates.

## Escopo
- Geração de embeddings para nome normalizado e local quando disponíveis.
- Cálculo de similaridade (cosine) e composição com `fuzz.ratio` existente.
- Respeitar `time_tolerance_minutes` e categorias.
- Métricas de impacto (duplicatas removidas vs baseline).

## Critérios de Aceite
- [ ] Não regredir determinismo de `_select_best_event()`.
- [ ] Melhorar recall/precisão de dedup comparado ao baseline.
- [ ] Opt-in via `ai.enabled` respeitado; desativado mantém pipeline atual.
- [ ] Threshold configurável via `ai.thresholds.dedup` (default 0.85).
- [ ] Testes de integração cobrindo falsos positivos/negativos mais comuns.

## Plano de Resolução (proposto)
1) Integração no `EventProcessor`
- Adicionar caminho semântico em `_are_events_similar()` quando `ai.enabled=true`.
- Normalizar campos comparáveis (nome/local) antes de gerar embeddings.

2) Similaridade e score composto
- Calcular cosine similarity entre textos normalizados.
- Combinar com o score fuzzy existente (ex.: média ponderada): `score = w_sem*semantic + w_fuzzy*fuzzy` (default: 0.5/0.5; parametrizável futuro se necessário).
- Aplicar threshold `ai.thresholds.dedup` no score composto.

3) Restrições e regras existentes
- Respeitar `time_tolerance_minutes` e filtros por categoria; não alterar `_select_best_event()`.

4) Configuração e validação
- Reusar validação em `src/utils/config_validator.py` para `ai.enabled` e `ai.thresholds.dedup`.
- Respeitar `ai.batch_size` no processamento em lote, se aplicável.

5) Testes e documentação
- Criar testes de integração com pares quase-duplicados e não-duplicados (FP/FN típicos).
- Documentar comportamento, configuração e troubleshooting em `docs/CONFIGURATION_GUIDE.md` e README.
- Atualizar `CHANGELOG.md` e `RELEASES.md`.

## Resultados — Verificações (a preencher durante a execução)
- `_are_events_similar()` combina fuzzy+semântico sob `ai.enabled`.
- Threshold aplicado corretamente (`ai.thresholds.dedup`).
- Determinismo preservado em `_select_best_event()`.
- Testes de integração passando.
- Métricas de impacto registradas.

## Checklist de Execução
- [x] Branch criada: `feat/160-semantic-dedup`.
- [x] Artefatos locais criados: `docs/issues/open/issue-160.md` e `.json`.
- [ ] Plano confirmado para iniciar implementação.
- [ ] Implementação da deduplicação semântica com score composto.
- [ ] Testes unitários/integrados ajustados.
- [ ] Documentação e release notes atualizadas.

## Logs e Referências
- Arquivos: `src/event_processor.py`, `src/utils/config_validator.py`, `motorsport_calendar.py`, `docs/architecture/ai_implementation_plan.md`, `docs/CONFIGURATION_GUIDE.md`, `CHANGELOG.md`, `RELEASES.md`.
- Issue GH: https://github.com/dmirrha/motorsport-calendar/issues/160
- Epic relacionada: #157

## Status
- Aberta; pronta para implementação após confirmação do plano.
