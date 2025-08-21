# Issue 131 — P0: Habilitar gate de cobertura de patch (≥85%) no Codecov (informativo)

- ID: 3337053812
- Número: 131
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/131
- Criado em: 2025-08-20T08:13:43Z
- Atualizado em: 2025-08-20T08:13:43Z
- Labels: enhancement, ci, coverage, needs-triage, priority: P0

## Contexto
A auditoria destacou a necessidade de gate para cobertura de patch. Etapa inicial deve ser informativa para maturar o processo.

## Objetivo
Configurar `codecov.yml` para ativar o status de `patch` com limiar ≥85% em modo informativo (sem bloquear merges inicialmente).

## Escopo
- Atualizar `codecov.yml`: seção `coverage.status.patch` com `informational: true`, `target: 85%`.
- Validar no CI que o status aparece nos PRs.
- Documentar no README/overview como interpretar os checks.

## Critérios de Aceite
- Check de `patch` aparece nos PRs com target de 85%.
- Não bloqueia merges nesta fase (informational true).
- Documentação atualizada.

## Tarefas (da issue)
- [ ] Ajustar `codecov.yml`.
- [ ] Validar em PR de teste.
- [ ] Atualizar docs.

---

# Plano de Resolução (proposto)

## 1) Configuração do Codecov
- Arquivo: `codecov.yml`
- Ajustar a seção `coverage.status.patch.default` para:
  - `informational: true` (já presente)
  - `target: 85%` (novo)
- Manter `coverage.status.project.default.informational: true` como está.

## 2) Validação em PR
- Abrir PR de teste tocando um arquivo leve (ex.: doc) para acionar o Codecov.
- Confirmar que o check “patch” aparece com target 85% e status informativo.

## 3) Documentação
- Arquivos: `README.md` e `docs/tests/overview.md`
- Adicionar uma subseção “Gate de cobertura de patch (Codecov)” explicando:
  - O que é “patch coverage” e o limiar de 85%.
  - Que o check é informativo nesta fase (não bloqueia).
  - Como interpretar o relatório do Codecov no PR.
- Notas de versão: `CHANGELOG.md` e `RELEASES.md` (marcar como patch release; coordenação com PR #110 para consolidar doc no último passo antes do merge).

## 4) Riscos e Mitigações
- Flutuação de cobertura em patches pequenos: documentar limites e ajustar futuramente (ex.: `threshold`).
- Ruído inicial em PRs: manter “informational” até estabilizar o processo, depois avaliar tornar required.

## Checklist de Execução
- [ ] Atualizar `codecov.yml` (target 85% em `coverage.status.patch.default`).
- [ ] Abrir PR e validar check do Codecov (patch ≥85%).
- [ ] Atualizar `README.md` e `docs/tests/overview.md` com instruções de interpretação.
- [ ] Atualizar `CHANGELOG.md` e `RELEASES.md`.
- [ ] PR com “Closes #131” e CI verde.

---

## Confirmação
Autoriza aplicar o plano acima na branch `issue/131-codecov-patch-gate-85` (editar `codecov.yml` e abrir PR de validação)?
