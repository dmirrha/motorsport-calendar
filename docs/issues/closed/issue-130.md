# Issue 130 — P0: Adicionar pytest-timeout e pytest-randomly para estabilidade e ordem não determinística

- ID: 3337053740
- Número: 130
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/130
- Criado em: 2025-08-20T08:13:41Z
- Atualizado em: 2025-08-20T08:13:41Z
- Labels: enhancement, ci, testing, needs-triage, priority: P0

## Contexto
A auditoria recomendou configurar timeouts por teste e embaralhar a ordem de execução para expor dependências entre testes e travamentos.

## Objetivo
- Introduzir `pytest-timeout` (ex.: 60s default, sobrescritível por marker).
- Introduzir `pytest-randomly` (seed controlada + log da seed no output de CI).

## Escopo
- Ajustar `pytest.ini` com opções padrão (timeout, randomly).
- Atualizar pipelines de CI (`.github/workflows/tests.yml`) para exibir seed e tornar falhas reprodutíveis.
- Documentar em `docs/tests/overview.md` como reproduzir localmente com a seed do CI.

## Critérios de Aceite
- Timeouts aplicados na suíte (com exceções documentadas via markers).
- Ordem dos testes embaralhada por padrão; seed registrada no log.
- Documentação atualizada.

## Tarefas (da issue)
- [ ] Adicionar dependências aos requirements (dev) se necessário.
- [ ] Configurar `pytest.ini` (timeout e randomly).
- [ ] Atualizar workflow para logar seed e reutilizá-la em reruns.
- [ ] Atualizar docs.

---

# Plano de Resolução (proposto)

## 1) Dependências (dev)
- Arquivo: `requirements-dev.txt`
- Adições:
  - `pytest-timeout~=2.3`
  - `pytest-randomly~=3.15`
- Observação: manter `pytest~=8.0` e `pytest-cov~=5.0` já existentes. Não alterar `requirements.txt` para evitar impacto em runtime.

## 2) Configuração do Pytest
- Arquivo: `pytest.ini`
- Ajustes em `addopts`:
  - Adicionar: `--timeout=60` (default global)
  - Adicionar: `--timeout-method=thread` (mais portável e segura para threads)
  - Habilitar randomização via plugin (sem seed fixa no ini). A seed será injetada via CLI no CI.
- Documentar exceptions por marcador:
  - Para casos que precisem mais tempo: usar `@pytest.mark.timeout(120)` ou valor apropriado por teste.

## 3) Pipeline de CI
- Arquivo: `.github/workflows/tests.yml`
- Em todos os jobs que invocam pytest (`tests`, `integration`, `e2e_happy`):
  - Definir `SEED=${{ github.run_id }}`.
  - Logar: `echo "Pytest randomly seed: $SEED"`.
  - Invocar: `pytest ... --randomly-seed="$SEED" ...` (mantendo os argumentos atuais).
- Benefício: seed determinística por execução, reproduzível a partir do log e do run_id.

## 4) Documentação
- Arquivo: `docs/tests/overview.md`
- Adicionar subseção: "Execução não determinística e seed (pytest-randomly)" contendo:
  - Explicação de que a ordem é embaralhada por padrão pela CI.
  - Onde encontrar a seed no log do workflow.
  - Como reproduzir localmente: `pytest --randomly-seed=<SEED_DO_CI>`.
  - Como ajustar timeouts por teste via marker `@pytest.mark.timeout(...)`.

## 5) Notas de versão
- Atualizar `CHANGELOG.md` (seção [Unreleased]) e `RELEASES.md` (Não Lançado) com a entrada:
  - "CI/Tests: adicionados pytest-timeout (60s default) e pytest-randomly (seed logada no CI); documentação atualizada."

---

## Riscos e Mitigações
- Mudança de ordem pode expor flaky tests: CI exibirá a seed para reprodução. Ajustar testes conforme necessário.
- Timeouts podem falhar em casos legítimos mais lentos: usar marker `@pytest.mark.timeout(N)` nos casos excepcionais.

## Checklist de Execução
- [ ] Atualizar requirements-dev
- [ ] Atualizar pytest.ini
- [ ] Atualizar .github/workflows/tests.yml (3 jobs)
- [ ] Atualizar docs/tests/overview.md
- [ ] Atualizar CHANGELOG.md e RELEASES.md
- [ ] Commitar, abrir PR com "Closes #130" e validar CI

---

## Confirmação
Autoriza aplicar o plano acima na branch `issue/130-pytest-timeout-randomly`?
