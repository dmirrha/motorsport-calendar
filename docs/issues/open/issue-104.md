# Issue #104 — Configuração de componentes do Codecov

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/104
- Docs Codecov (Components): https://docs.codecov.com/docs/components
- Workflow: `.github/workflows/tests.yml`
- Plano de testes: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Configurar componentes no Codecov para visualizar cobertura por áreas do sistema. Manter o pipeline atual (uploads por flags `unit`/`integration`/`e2e` via OIDC e `disable_search: true`).

## Escopo
- Adicionar definição de componentes no `codecov.yml` conforme documentação oficial.
- Mapear diretórios/fonte do projeto em componentes lógicos (ex.: Parser/Processamento/Utils/UI/etc.).
- Garantir que a configuração não conflita com flags existentes nem com `disable_search: true`.
- Atualizar documentação (README, `docs/TEST_AUTOMATION_PLAN.md`, `tests/README.md`).

## Proposta de Componentes (inicial)
- `core-processing`: `src/event_processor.py`, `src/category_detector.py`, `src/silent_period.py`
- `calendar-generation`: `src/ical_generator.py`
- `data-collection`: `src/data_collector.py`
- `configuration`: `src/config_manager.py`
- `ui`: `src/ui_manager.py`
- `utils`: `src/utils/`
- `logging`: `src/logger.py`

Atualização: incluído componente adicional `sources` (paths: `sources/`) para cobrir arquivos referenciados por relatórios de cobertura (especialmente e2e/integration), evitando itens "unassigned".

Nota: A sintaxe exata no `codecov.yml` será confirmada na documentação oficial antes do commit (evitar configurações depre­cadas). A ideia é usar o bloco de “components”/“component_management” com lista de componentes e seus `paths`.

## Tarefas
- [x] Entender como configurar o Codecov por componentes (confirmar sintaxe atual na doc)
- [x] Realizar a configuração no `codecov.yml` (adicionar componentes, incluindo `sources/`)
- [ ] Executar o CI e validar no dashboard (slug `/github`) a separação por componentes
- [x] Atualizar documentação (README, `docs/TEST_AUTOMATION_PLAN.md`, `tests/README.md`) — links ajustados para `/github`; seção de Components e Test Analytics adicionada
- [ ] Abrir PR referenciando “Closes #104” e sincronizar checklist

## Critérios de Aceite
- [ ] Dashboard do Codecov exibe métricas por componente
- [ ] `codecov.yml` atualizado com mapeamento de componentes e carregado sem warnings
- [ ] CI conclui com sucesso; uploads (flags `unit`/`integration`/`e2e`) seguem com HTTP 200
- [ ] Documentação atualizada com instruções de uso/visualização

## Riscos e Observações
- Configurações antigas de `paths` por flag estavam incorretas; manteremos flags sem `paths` e adicionaremos componentes por diretórios de código-fonte.
- `disable_search: true` permanece; componentes agregam cobertura por path dos arquivos-fonte já presentes nos relatórios.
 - Test Analytics configurado via `codecov/test-results-action@v1` (envio de `junit.xml` por job). Requer `CODECOV_TOKEN` em GitHub Secrets.

## Plano de Validação
1) Abrir PR a partir da branch `chore/issue-104` com o `codecov.yml` atualizado.
2) Disparar workflow “Tests” (manual `workflow_dispatch`).
3) Verificar no link do commit no Codecov (slug `/github`) a presença de “Components” e métricas por componente.

## Confirmação
Solicito confirmação para:
- Implementar os componentes no `codecov.yml` conforme proposta acima (ajustando sintaxe pela doc atual).
- Atualizar a documentação correspondente e abrir a PR referenciando “Closes #104”.
