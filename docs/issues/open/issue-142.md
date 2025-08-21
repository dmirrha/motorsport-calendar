# Issue 142 — P1: Elevar gradualmente o gate global de cobertura (+5pp por release até 75–80%)

- ID: 3341577998
- Número: 142
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/142
- Criado em: 2025-08-21T12:35:31Z
- Atualizado em: 2025-08-21T12:35:31Z
- Labels: enhancement, ci, coverage, needs-triage, priority: P1

## Contexto
A auditoria recomenda aumentar o gate global de cobertura de forma incremental. O gate de patch (≥85%) já foi habilitado como informativo (#131). Próximo passo: elevar o gate global progressivamente.

## Objetivo
Aplicar incremento de +5pp por release até atingir ~75–80% de cobertura global, sem travar o fluxo de PRs prematuramente.

## Escopo
- Definir baseline atual de cobertura global.
- Ajustar limiares nos jobs:
  - `pytest --cov-fail-under=<novo_limite>` nos jobs relevantes; ou
  - `codecov.yml` (project target) informativo e `--cov-fail-under` como gate hard.
- Monitorar impactos em PRs e ajustar documentação.

## Critérios de Aceite
- Primeiro incremento aplicado e validado no CI.
- Documentação atualizada (`README.md`, `docs/tests/overview.md`) explicando a estratégia incremental.
- Notas em `CHANGELOG.md` e `RELEASES.md`.

## Tarefas (da issue)
- [ ] Medir baseline atual e definir próximo limite (+5pp).
- [ ] Atualizar workflows de teste com o novo `--cov-fail-under` (ou equivalente).
- [ ] Validar em PR.
- [ ] Atualizar documentação e notas de release.

---

# Plano de Resolução (proposto)

## 1) Medição e definição de alvo
- Executar local/CI: `pytest --cov=src --cov-report=term-missing` para obter baseline atual.
- Definir `next_limit = baseline + 5pp`.

## 2) Aplicação do gate
- Preferência: aplicar `--cov-fail-under=<next_limit>` no(s) job(s) de teste.
- Manter `codecov.yml` project status informativo; usar Codecov para visibilidade e tendência.

## 3) Validação
- Abrir PR de ajuste de limite e validar verde no CI.
- Caso falhe, identificar módulos críticos para elevar cobertura mínima.

## 4) Documentação
- Atualizar `README.md` e `docs/tests/overview.md` com a política de incremento +5pp/release.
- Atualizar `CHANGELOG.md` e `RELEASES.md`.

## Riscos e Mitigações
- Aumento de fricção em PRs: começar com limites realistas; ajustar gradualmente.
- Oscilação de cobertura: considerar margem (ex.: thresholds em Codecov) e guias de escrita de testes.

## Checklist de Execução
- [ ] Baseline medido e próximo limite definido.
- [ ] CI configurado com novo `--cov-fail-under`.
- [ ] PR de validação aprovado.
- [ ] Documentação e notas atualizadas.

---

## Status
- Aberta; aguardando priorização/triagem.
