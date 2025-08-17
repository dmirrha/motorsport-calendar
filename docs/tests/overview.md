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
- Local (Makefile recomendado):
  - Suíte completa (usa addopts do `pytest.ini`: cobertura HTML/XML, JUnit, gate 45%): `make test`
  - Somente unit: `make test.unit`
  - Somente integração: `make test.integration`
  - Cobertura no terminal (linhas faltantes): `pytest --cov --cov-report=term-missing -q`
  - Abrir relatório HTML (macOS): `open htmlcov/index.html`
- Sem falha por cobertura (override local): `PYTEST_ADDOPTS="--cov-fail-under=0" pytest`
- CI: GitHub Actions (`.github/workflows/tests.yml`) usando as mesmas opções do `pytest.ini`.

## Estrutura de pastas
- `tests/unit/`: testes unitários por módulo.
- `tests/fixtures/`: insumos estáticos (ex.: `ical/` com snapshots canônicos).
- `tests/utils/`: utilitários de teste (ex.: normalização/ comparação de ICS).

## Cenários
- Índice de cenários por fase: `docs/tests/scenarios/SCENARIOS_INDEX.md`

## Atualizações recentes
- CategoryDetector: teste adicional cobrindo branches previamente não exercitados em `src/category_detector.py` (normalização vazia, mapeamentos custom e aprendizado a partir de arquivo salvo). Arquivo: `tests/unit/category/test_category_detector_additional_coverage.py`. Resultado: 100% no run focado.
- DataCollector: teste unitário para o caminho de timeout na coleta concorrente, garantindo marcação de erro e atualização de estatísticas. Arquivo: `tests/unit/data_collector/test_data_collector_timeout_not_done.py`. Resultado: 100% no run focado.

## Referências
- Governança Fase 2: PR #87 (https://github.com/dmirrha/motorsport-calendar/pull/87) — épico #78
