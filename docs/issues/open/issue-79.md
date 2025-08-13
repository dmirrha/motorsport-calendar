# Issue #79 — Fase 2 — Mocks/Fakes de Coleta e Controle de Tempo

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/79
- Regras: `.windsurf/rules/tester.md`

## Descrição
Fornecer mocks/fakes mínimos para rede, tempo e aleatoriedade para tornar testes determinísticos.

## Tarefas
- [x] Fake de coleta (substitui requests/HTTP com dados locais)
- [x] Controle de tempo (ex.: freezegun ou wrapper de tempo existente)
- [x] Estabilizar aleatoriedade/UID quando aplicável
- [x] Instruções de uso nas fixtures/utilitários

## Critérios de Aceite
- [x] Testes não acessam rede/FS externo
- [x] Execução determinística 3× local
- [x] Documentação em `tests/README.md`

## Plano de Resolução (Fase 2 — Mocks/Fakes)
 
 - Estrutura
   - Fake de coleta HTTP: patch de `requests.get`/cliente com dados locais em `tests/data/` e helpers simples.
   - Controle de tempo: wrapper `time_provider` injetável; em testes, usar freezegun ou stub.
   - Aleatoriedade/UID: seed fixo para `random`; stub para `uuid4()` quando necessário.
 
 - Estratégia de testes
   - Testes unitários para parsers e camadas que consomem os fakes.
   - Mocks mínimos via `unittest.mock.patch`.
   - Casos de erro comuns: timeout, 404, HTML malformado.
 
 - Fixtures/utilitários
   - Fixtures em `tests/conftest.py` para fakes de rede/tempo.
   - Dados de exemplo em `tests/data/`.
 
 - Métricas e critérios
   - 3× execução local sem flakes, <30s.
   - Sem acesso à rede/FS externo.
   - Documentar comandos em `tests/README.md`.
 
 - Branch de trabalho: `chore/issue-79-fakes-phase2`
 - PR: #90 (https://github.com/dmirrha/motorsport-calendar/pull/90)
 
## Progresso
- [x] Estrutura de fakes definida
- [x] Execução estável confirmada 3× (<30s)
- [x] Documentação sincronizada
