# Issue #64 — Fase 1.1: Documentação e Cenários (sincronismo)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/64
 - PR (draft): https://github.com/dmirrha/motorsport-calendar/pull/73

## Objetivo
Elevar a qualidade da suíte de testes, priorizando confiabilidade sobre números. Foco em parsers, validadores e processadores de dados, garantindo:
- Determinismo (<30s local) e isolamento de rede/FS/TZ/random com mocks simples
- Cobertura de cenários críticos de erro (timeout, 404, HTML malformado, dados faltantes)
- Oráculos claros e asserts diretos
- Documentação e rastreabilidade sincronizadas a cada incremento

Meta de cobertura derivada (não-fim): atingir ≥ 80% quando a qualidade estiver comprovada.

## Plano de Qualidade
1. Análise de risco e foco
   - `sources/tomada_tempo.py`: variações de HTML e datas
   - `src/category_detector.py`: normalização/ambiguidade de categorias
   - `src/config_manager.py`: overrides por env, chaves faltantes, tipos inválidos
   - `src/utils/payload_manager.py`: payloads incompletos/tipos errados
   - `src/ical_generator.py`: campos ICS obrigatórios/TimeZone ausente
2. Cenários críticos a testar
   - Happy path mínimo por módulo e erros comuns (404/timeout/HTML malformado/dados faltantes)
3. Oráculos e verificação
   - Asserts diretos; validações de estrutura/valores; uso de fixtures simples
4. Determinismo e isolamento
   - Sem IO/rede reais; mocks de requests/FS; fixar TZ e random quando aplicável
5. Entregas iterativas
   - Após cada incremento: atualizar `docs/tests/scenarios/*.md`, `docs/TEST_AUTOMATION_PLAN.md`, `CHANGELOG.md`, `RELEASES.md`
6. Gate de cobertura
   - Manter o gate atual até estabilizar a qualidade; elevar somente após suíte estável e rápida

## PARE — Autorização
- PR inicia em draft até validação deste plano.
 
## Critérios de Aceite
- Suíte determinística (<30s local)
- Cenários críticos cobertos nos módulos foco (incluindo erros comuns)
- Zero flakes em 3 execuções locais consecutivas
- Documentação e rastreabilidade sincronizadas a cada incremento
- Cobertura global resultante ≥ 70% antes de elevar gate; objetivo final ≥ 80% quando a qualidade estiver comprovada

## Progresso
- [x] Branch criada
- [x] PR (draft) aberta — PR #73: https://github.com/dmirrha/motorsport-calendar/pull/73
 - [x] Documentação atualizada
  - [x] Releases/Changelog atualizados

### Incremento atual: P2 — CategoryDetector (Concluído)

- Testes adicionados:
  - Persistência: `save_learned_categories` e `load_learned_categories` com mock de filesystem (`tmp_path`), incluindo cenários de erro.
  - Estatísticas: `get_statistics` com agregação por fonte e categoria após múltiplas detecções.
- Ajustes no algoritmo:
  - `detect_category`: matches exatos têm prioridade determinística sobre fuzzy (evita fuzzy 1.0 sobrepor exato); aprendizado controlado; stats atualizadas.
  - `detect_categories_batch`: tentar primeiro `raw_category` isolado; combinar com `name` apenas se necessário.
- Métricas:
  - Suíte: **258 passed**; cobertura global: **67.78%**
  - Módulo `src/category_detector.py`: ~**96%** de cobertura
  - Estabilidade confirmada **3×** (<30s)
- Sincronismo de documentação/PR:
  - Atualizados: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`
  - PR #73 (draft) atualizado na branch `chore/issue-64-coverage-80`

### Incremento atual: P6 — Logger (Concluído)

- Testes adicionados:
  - `tests/unit/logger/test_logger_basic.py`
  - `tests/unit/logger/test_logger_misc.py`
- Escopo coberto:
  - Inicialização/configuração (handlers, formatters, níveis por saída), rotação de logs
  - Emissão de níveis: success/error/warning/info/debug
  - `save_payload` (json/html/text), incluindo caminhos de exceção
  - `set_console_level`, `get_logger`, resumo/finalização de execução
  - Helpers de domínio: category detection, remoção de duplicados, weekend, iCal, eventos por fonte (com fallbacks de config)
- Estratégia:
  - Isolamento total de I/O real (uso de `tmp_path`)
  - Monkeypatch para desabilitar `_cleanup_old_logs` e `_cleanup_rotated_logs`
  - Handlers custom para capturar registros e assertar conteúdo
- Métricas:
  - Módulo `src/logger.py`: **83%**
  - Suíte: **295 passed**
  - Cobertura global: **83.35%**
  - Estabilidade confirmada **3×** (<30s)
- Sincronismo de documentação/PR:
  - Atualizados: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`
  - Versão: bump para `0.5.8` em `src/__init__.py`
  - PR #73 (draft) atualizado na branch `chore/issue-64-coverage-80`
- Próximos passos:
  - P3 — `src/utils/error_codes.py`: cobrir mapeamentos, mensagens de fallback e tipos inválidos.

### Incremento atual: P3 — ErrorCodes (Concluído)

- Testes adicionados:
  - `tests/unit/utils/test_error_codes.py` cobrindo mapeamentos específicos de `get_error_suggestions`, fallback para códigos desconhecidos e tipos inválidos, e extração de severidade em `get_error_severity` (Enum vs string via `.value`).
- Métricas:
  - Suíte: **267 passed**; cobertura global: **68.04%**
  - Módulo `src/utils/error_codes.py`: > **90%** de cobertura
  - Estabilidade confirmada **3×** (<30s)
- Sincronismo de documentação/PR:
  - Atualizados: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`
  - PR #73 (draft) atualizado na branch `chore/issue-64-coverage-80`
- Próximos passos:
  - P4 — `src/data_collector.py`: cobrir fluxos críticos mínimos com mocks (sem rede), erros comuns (timeout/404) e validação de dados obrigatórios.

### Incremento atual: P4 — DataCollector (Concluído)

- Testes adicionados (sem rede real):
  - Fluxos críticos com concorrência (coleta em paralelo) e cancelamento/remoção de fonte.
  - Estatísticas e estados internos após coletas múltiplas.
  - Erros comuns: timeout/404 com retry/backoff simulados e asserts de estado.
- Métricas:
  - Módulo `src/data_collector.py`: ~**67%**
  - Suíte: **272–277 passed** (histórico); cobertura global: **~72%**
  - Estabilidade confirmada **3×** (<30s)
- Sincronismo de documentação/PR:
  - Atualizados: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`
  - PR #73 (draft) atualizado na branch `chore/issue-64-coverage-80`

### Incremento atual: P5 — UIManager (Concluído)

- Testes adicionados:
  - `tests/unit/ui_manager/test_ui_manager_basic.py`
  - `tests/unit/ui_manager/test_ui_manager_more.py`
- Escopo coberto:
  - Progressão de etapas (`start_step_progress`/`show_step`), resumos de eventos, agrupamento por categoria.
  - Mensagens: sucesso, erro, aviso e resultado de etapa.
  - Geração de iCal e instruções de importação.
  - Flags de UI: cores/ícones/desabilitado (sem I/O real via fakes de console/progresso).
- Métricas:
  - Módulo `src/ui_manager.py`: **100%**
  - Diretório `ui_manager`: **13 testes**
  - Estabilidade confirmada **3×** (<30s)
- Sincronismo de documentação/PR:
  - Atualizados: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`
  - PR #73 (draft) atualizado na branch `chore/issue-64-coverage-80`

### Prioridades — Módulos abaixo de 80% (12/08/2025)

1) `src/category_detector.py` — 69%
   - Foco: fallback "Unknown", conflitos de regras, métricas/estatísticas, persistência (save/load).

2) `src/utils/error_codes.py` — 76%
   - Foco: caminhos de erro e mapeamentos pouco exercitados.

3) `src/data_collector.py` — 67%
  - Foco: fluxos críticos mínimos isolados com mocks (adiar casos pesados).

 - [x] Cobertura unitária ≥ 80% (meta)
