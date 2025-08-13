# Guia de Contribuição

 > Política vigente (CI ativo)
 >
 > - CI (GitHub Actions) ativo: pytest + cobertura + artefatos.
 > - SemVer adotado: cada commit testado incrementa a versão (0.x.y até 1.0.0).
 > - Toda mudança deve vir acompanhada de atualização de documentação e changelog.

## Fluxo de Trabalho para Commits

### 1. Antes de Fazer um Commit
- [ ] Executar a suíte 3× sem flakes (< 30s por execução)
- [ ] Paridade local/CI: use os mesmos comandos do `README.md`/`tests/README.md`
- [ ] Atualizar documentação obrigatória (conforme aplicável):
  - `CHANGELOG.md`, `RELEASES.md`
  - `README.md`, `CONTRIBUTING.md`
  - `PROJECT_STRUCTURE.md`, `DATA_SOURCES.md`, `REQUIREMENTS.md`, `CONFIGURATION_GUIDE.md`
  - `docs/TEST_AUTOMATION_PLAN.md`, `tests/README.md`
- [ ] Sincronizar rastreabilidade da issue: `docs/issues/open/issue-<n>.md` e `.json`
- [ ] Garantir cobertura por testes para as mudanças
- [ ] Versionamento SemVer: avaliar incremento em `src/__init__.py`

### 2. Mensagens de Commit
Use o formato convencional de commits:
```
tipo(escopo): descrição curta

Corpo detalhado explicando as mudanças

Refs: #número-da-issue
```

- Referencie issues e PRs: use `Refs: #<n>` nos commits; no PR, use `Closes #<n>` para fechamento automático da issue.

**Tipos de commit:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Formatação, ponto e vírgula, etc. (não altera código)
- `refactor`: Refatoração de código
- `test`: Adição ou modificação de testes
- `chore`: Atualização de tarefas, configurações, etc.

### 3. Atualização de Documentação
- **CHANGELOG.md/RELEASES.md**: registre mudanças significativas e notas acumulativas
- **README.md/tests/README.md**: reflita novas funcionalidades e estratégia de testes/mocks
- **PROJECT_STRUCTURE.md/DATA_SOURCES.md/REQUIREMENTS.md/CONFIGURATION_GUIDE.md**: mantenha coerência
- **docs/TEST_AUTOMATION_PLAN.md**: mantenha a estratégia/estado dos testes atualizada

### 4. Versionamento
- Siga o [Versionamento Semântico](https://semver.org/)
- Política: cada commit testado incrementa a versão (0.x.y até 1.0.0)
- Atualize a versão em `src/__init__.py` e documentos correlatos
- Crie uma tag Git para cada release

## Processo de Code Review
1. Abra o PR como draft e referencie a issue (ex.: `Closes #<n>`)
2. Confirme checklist concluído (docs, rastreabilidade, versão, testes 3× < 30s)
3. Marque como "Ready for review" quando CI estiver verde e docs sincronizados
4. Resolva todos os comentários e mantenha o changelog/notas de release atualizados
5. Após aprovação, realize o merge conforme política do repositório

## Padrões de Código
- Siga as convenções de estilo do Python (PEP 8)
- Documente funções e classes com docstrings
- Mantenha os testes atualizados

## Reportando Problemas
- Verifique se o problema já existe
- Forneça informações detalhadas sobre o ambiente
- Inclua etapas para reproduzir o problema
- Adicione logs e capturas de tela, se aplicável
