# P0: Habilitar gate de cobertura de patch (≥85%) no Codecov (informativo)

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

## Tarefas
- [ ] Ajustar `codecov.yml`.
- [ ] Validar em PR de teste.
- [ ] Atualizar docs.

## Referências
- `docs/tests/audit/TEST_AUDIT_2025-08-19.md`
- `codecov.yml`
- Issue relacionada: #98
