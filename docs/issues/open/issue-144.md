# Issue 144 — P1: Mutation testing baseline (mutmut) em módulos críticos (event_processor, ical_generator, base_source)

- ID: 3341578859
- Número: 144
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/144
- Criado em: 2025-08-21T12:35:47Z
- Atualizado em: 2025-08-21T12:35:47Z
- Labels: enhancement, ci, testing, needs-triage, priority: P1

## Contexto
A auditoria (P1) apontou risco de cobertura otimista. Baseline de mutation testing mede a efetividade dos testes além do percentual de cobertura.

## Objetivo
Configurar `mutmut` para avaliar mutantes em módulos críticos:
- `src/event_processor.py`
- `src/ical_generator.py`
- `sources/base_source.py`

## Escopo
- Adicionar `mutmut` ao `requirements-dev.txt`.
- Criar alvo local: `make mutmut-baseline` (ou script) com caminhos de mutação.
- Ajustes de performance: ignorar testes lentos, limitar escopo inicial.
- CI opcional (noturno) em modo informativo (sem bloquear PRs).

## Critérios de Aceite
- Execução local gera relatório de mutantes (≥1 módulo avaliado).
- Documentação adicionada (`tests/README.md`, `docs/tests/overview.md`) com instruções e interpretação.
- Sem impacto negativo no tempo dos jobs de PR.

## Tarefas (da issue)
- [ ] Adicionar `mutmut` ao `requirements-dev.txt`.
- [ ] Criar alvo `mutmut-baseline` (Makefile/script) e instruções.
- [ ] (Opcional) Integrar job noturno informativo no CI.
- [ ] Atualizar documentação e notas (CHANGELOG/RELEASES).

---

# Plano de Resolução (proposto)

## 1) Dependência e comando
- requirements-dev: adicionar `mutmut`.
- Comando inicial sugerido:
  - `mutmut run --paths-to-mutate src/event_processor.py,src/ical_generator.py,sources/base_source.py --backup`

## 2) Execução e limites
- Rodar localmente; ajustar se necessário (ex.: `--use-coverage` após primeira passada para acelerar).
- Documentar leitura de `mutmut results` e priorização de mutantes sobreviventes.

## 3) CI informativo (opcional)
- Job noturno somente relatório (sem gate de falha), publicar artefatos.

## 4) Documentação
- Adicionar seção “Mutation testing (mutmut)” em `docs/tests/overview.md` e exemplos no `tests/README.md`.

## Riscos e Mitigações
- Tempo de execução: começar pequeno (3 módulos), depois expandir.
- Ruído inicial: focar nos mutantes de maior risco (parsers/dedupe/ordenadores) primeiro.

## Checklist de Execução
- [ ] Dependência adicionada.
- [ ] Comando/Make alvo criado.
- [ ] Execução local validada.
- [ ] (Opcional) CI noturno informativo.
- [ ] Documentação/Notas atualizadas.

---

## Status
- Aberta; aguardando priorização/triagem.
