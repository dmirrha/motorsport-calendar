# P0: Adicionar pytest-timeout e pytest-randomly para estabilidade

## Contexto
A auditoria recomendou configurar timeouts por teste e embaralhar a ordem de execução para expor dependências entre testes e travamentos.

## Objetivo
- Introduzir `pytest-timeout` (ex.: 60s default, overridable por marker).
- Introduzir `pytest-randomly` (seed controlada + log da seed no output de CI).

## Escopo
- Ajustar `pytest.ini` com opções padrão (timeout, randomly).
- Atualizar pipelines de CI (`.github/workflows/tests.yml`) para exibir seed e tornar falhas reprodutíveis.
- Documentar em `docs/tests/overview.md` como reproduzir localmente com a seed do CI.

## Critérios de Aceite
- Timeouts aplicados na suíte (com exceções documentadas via markers).
- Ordem dos testes embaralhada por padrão; seed registrada no log.
- Documentação atualizada.

## Tarefas
- [ ] Adicionar dependências aos requirements (dev) se necessário.
- [ ] Configurar `pytest.ini` (timeout e randomly).
- [ ] Atualizar workflow para logar seed e reutilizá-la em reruns.
- [ ] Atualizar docs.

## Referências
- `docs/tests/audit/TEST_AUDIT_2025-08-19.md`
- `.github/workflows/tests.yml`
