# Documentação de Testes — Overview

Objetivo: descrever a estratégia mínima de testes para o projeto, com foco em simplicidade, rastreabilidade e execução rápida/estável.

## Estratégia
- Priorizar testes unitários para parsing, validação e processamento de dados.
- Cobertura alvo por módulo definida por issue/épico vigente.
- Evitar I/O real; preferir fakes/mocks e `tmp_path`.
- Estabilidade: 3× sem flakes, <30s local.

## Escopo
- Fase 0: inventário e decisões de limpeza/escopo.
- Fase 1: unit (parsers/validadores/utils).
- Fase 2: integração (fluxos principais: coleta → processamento → iCal).

## Como executar
- Local:
  - `pytest -q`
  - Relatório de cobertura com linhas faltantes: `pytest --cov --cov-report=term-missing`
  - Sem falha por cobertura: `pytest --cov --cov-fail-under=0`
  - Integração: `pytest -m integration -q`
- CI: segue configuração padrão do repositório (GitHub Actions) e critérios do épico/issue.

## Estrutura de pastas
- `tests/unit/`: testes unitários por módulo.
- `tests/fixtures/`: insumos estáticos (ex.: `ical/` com snapshots canônicos).
- `tests/utils/`: utilitários de teste (ex.: normalização/ comparação de ICS).

## Cenários
- Índice de cenários por fase: `docs/tests/scenarios/SCENARIOS_INDEX.md`

## Referências
- Governança Fase 2: PR #87 (https://github.com/dmirrha/motorsport-calendar/pull/87) — épico #78
