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

## Determinismo de ICS e snapshots
- Ordenação de eventos: VEVENTs ordenados determinísticamente por `datetime` (convertido para UTC; fallback para naive) e, em seguida, por `display_name`/`name` para desempate.
- Streaming links: `streaming_links` ordenados alfabeticamente e limitados a 3 na descrição do evento.
- Normalização de snapshots: UID fixo; remoção de `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID`; quebras de linha `\n`.
- Estabilidade: cada cenário deve passar 3× localmente sem flakes e em <30s.

## Integração — PayloadManager (Fase 2)
- Teste: `tests/integration/test_phase2_payload_manager.py`
- Escopo: serialização de payloads (JSON/HTML/binário), compressão `gzip`, limpeza por idade e por quantidade (retenção), e estatísticas agregadas por fonte.
- Estabilidade: execução local estável, sem flakes observados.
- Cobertura: suíte consolidada ~**91.75%** (visível no Codecov por job/flag).

## Referências
- Governança Fase 2: PR #87 (https://github.com/dmirrha/motorsport-calendar/pull/87) — épico #78
