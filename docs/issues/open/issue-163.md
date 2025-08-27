# Issue 163 — F1: Integração de categorização semântica (threshold 0.75)

- ID: 3356427465
- Número: 163
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/163
- Criado em: 2025-08-26T16:56:47Z
- Atualizado em: 2025-08-26T17:09:16Z
- Labels: enhancement, needs-triage, priority: P1, ai, category

## Contexto
Integrar categorização semântica por embeddings no `src/category_detector.py`, mantendo as heurísticas atuais (fuzzy/aliases/aprendizado) como fallback. O serviço de embeddings (issue #165) fornece `embed_texts()` e deve operar 100% local com determinismo, batching e cache (conforme PR de embeddings).

- Threshold alvo: `0.75`, configurável via `ai.thresholds.category`.
- Opt-in via `ai.enabled=true`.
- Expor `category_source` (ex: "semantic" | "heuristic") e `category_confidence` no resultado.

## Objetivo
- Melhorar a detecção de categoria por similaridade semântica, sem degradar a baseline atual.
- Controlar risco via opt-in, mantendo fallback heurístico confiável.
- Tornar auditável via logging da decisão (fonte+confiança).

## Escopo
- Ajustes no `src/category_detector.py` para adicionar o caminho semântico em `detect_categories_batch()` quando `ai.enabled=true`.
- Construção/caching de vetores de referência para cada categoria/alias.
- Cálculo de similaridade (cosine) texto→categoria e aplicação de threshold configurável.
- Combinação com heurísticas e definição da fonte/valor de confiança final.
- Logging estruturado da decisão.
- Testes de integração cobrindo idiomas/variações comuns.
- Atualização de documentação (configuração, uso, troubleshooting).

## Critérios de Aceite
- [ ] Precisão mínima conforme plano; não piorar baseline atual.
- [ ] `category_source` e `category_confidence` presentes e corretos.
- [ ] Opt-in via `ai.enabled` respeitado; desativado mantém pipeline atual.
- [ ] Threshold configurável em `ai.thresholds.category` (default 0.75).
- [ ] Testes de integração verdes.

## Plano de Resolução (proposto)
1) Integração no detector
- Adicionar caminho semântico em `detect_categories_batch()` quando `ai.enabled=true`.
- Carregar/gerar embeddings de referência das categorias e seus aliases; cachear no serviço.

2) Similaridade e decisão
- Calcular similaridade (cosine) entre o texto normalizado e cada vetor de categoria/alias.
- Selecionar melhor match e comparar com `ai.thresholds.category` (default 0.75).
- Se atingir threshold: definir categoria por "semantic" e `category_confidence`=score.
- Caso contrário: fallback para heurísticas atuais; fonte="heuristic"; confiança conforme heurístico.

3) Metadados e logging
- Incluir `category_source` e `category_confidence` no resultado retornado.
- Logging estruturado com: entrada, melhor candidato, score, threshold, fonte escolhida.

4) Configuração e validação
- Reusar validação em `src/utils/config_validator.py` para `ai.enabled` e `ai.thresholds.category`.
- Respeitar `ai.batch_size` no processamento.

5) Testes e documentação
- Criar/ajustar testes de integração cobrindo idiomas, aliases e variações frequentes.
- Documentar novos comportamentos e configuração em `docs/CONFIGURATION_GUIDE.md` e README.
- Atualizar `CHANGELOG.md` e `RELEASES.md`.

## Resultados — Verificações (a preencher durante a execução)
- `src/category_detector.py`: caminho semântico implementado com fallback e metadados.
- Embeddings de referência cacheados e reusados.
- Logs de decisão disponíveis.
- Testes de integração passando.
- Documentação atualizada.

## Checklist de Execução
- [x] Branch criada: `feat/163-semantic-categorization-integration`.
- [x] Artefatos locais criados: `docs/issues/open/issue-163.md` e `.json`.
- [ ] Plano confirmado para iniciar implementação.
- [ ] Integração semântica implementada com fallback.
- [ ] Testes unitários/integrados ajustados.
- [ ] Documentação e release notes atualizadas.

## Logs e Referências
- Arquivos: `src/category_detector.py`, `src/utils/config_validator.py`, `motorsport_calendar.py`, `docs/architecture/ai_implementation_plan.md`, `docs/CONFIGURATION_GUIDE.md`, `CHANGELOG.md`, `RELEASES.md`.
- Issue rascunho: `.github/import_issues/imported/163-semantic-categorization-integration.md`
- Issue GH: https://github.com/dmirrha/motorsport-calendar/issues/163
- Epic relacionada: #157

## Status
- Aberta; pronta para implementação após confirmação do plano.
