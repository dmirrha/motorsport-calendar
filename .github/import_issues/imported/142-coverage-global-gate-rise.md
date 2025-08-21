# P1: Elevar gradualmente o gate global de cobertura (+5pp por release até 75–80%)

## Contexto
A auditoria (P1) recomenda aumentar o gate global de cobertura de forma incremental. O gate de patch (≥85%) já foi habilitado como informativo (#131). Próximo passo: elevar o gate global progressivamente.

## Objetivo
Planejar e aplicar incremento de +5 pontos percentuais por release até atingir ~75–80% de cobertura global.

## Escopo
- Definir ponto de partida (ex.: 45%).
- Ajustar limiares nos jobs:
  - `pytest --cov-fail-under=<novo_limite>` nos jobs relevantes ou
  - `codecov.yml` (project target) como informativo e usar `--cov-fail-under` para o gate hard.
- Monitorar impactos em PRs e ajustar documentação.

## Critérios de Aceite
- Primeiro incremento aplicado e validado no CI.
- Documentação atualizada (`README.md`, `docs/tests/overview.md`) explicando estratégia incremental.
- Notas em `CHANGELOG.md` e `RELEASES.md`.

## Tarefas
- [ ] Medir baseline atual e definir próximo limite (+5pp).
- [ ] Atualizar workflows de teste com o novo `--cov-fail-under` (ou equivalente).
- [ ] Validar em PR.
- [ ] Atualizar documentação e notas de release.

## Referências
- Auditoria: `docs/tests/audit/TEST_AUDIT_2025-08-19.md` (linhas 79–82).
- Relacionado: Issue #131 (patch gate informativo).
