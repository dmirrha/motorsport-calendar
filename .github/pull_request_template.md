# Título do PR

Resumo conciso das mudanças propostas.

## Closes

- Closes #<número_da_issue>
  - Use esta linha para fechamento automático da issue relacionada. Você pode listar múltiplas: `Closes #123, Fixes #456`.

## Tipo de mudança

- [ ] feat (nova funcionalidade)
- [ ] fix (correção de bug)
- [ ] docs (documentação)
- [ ] tests (testes)
- [ ] ci (pipeline/infra de CI)
- [ ] chore/refactor (manutenção/refatoração)

## Detalhes técnicos

- Descreva as principais alterações de código/arquitetura.
- Destaque decisões de design, compatibilidade e migrações, se houver.

## Testes

- [ ] Testes unitários atualizados/adicionados
- [ ] Testes de integração atualizados/adicionados
- [ ] Determinismo mantido (sem flakiness, sem dependência de ordem)
- [ ] Snapshots/ICS estáveis (quando aplicável)
- Comandos usados (exemplos):
  - `pytest -m unit --maxfail=1 -q`
  - `pytest -m integration --maxfail=1 -q`
  - `pytest -m e2e --maxfail=1 -q`

## Checklist de conformidade

- [ ] SemVer: tipo de mudança e impacto validados (0.x.y até 1.0.0)
- [ ] Release Drafter: labels corretas adicionadas ao PR
- [ ] Documentação revisada/atualizada quando aplicável:
  - [ ] CHANGELOG.md (seção [Unreleased])
  - [ ] RELEASES.md (seção “Não Lançado”)
  - [ ] README.md
  - [ ] CONTRIBUTING.md
  - [ ] CONFIGURATION_GUIDE.md
  - [ ] DATA_SOURCES.md
  - [ ] PROJECT_STRUCTURE.md
  - [ ] REQUIREMENTS.md
  - [ ] Outros docs impactados
- [ ] CI verde (GitHub Actions)
- [ ] Cobertura verificada no Codecov (flags unit/integration/e2e visíveis; sem apontar `paths` para diretórios de testes)
- [ ] Rastreabilidade:
  - [ ] Referência a issues/PRs relacionados
  - [ ] Se aplicável, arquivos em `docs/issues/open/` atualizados (MD/JSON) ou movidos para `closed/`

## Itens de compatibilidade/migração (se aplicável)

- Impacto em configs (ex.: `config/config.example.json`)
- Notas de depreciação/migração

## Notas adicionais

- Contexto extra, decisões e próximos passos.
