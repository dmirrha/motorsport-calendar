# Guia de Contribuição

## Fluxo de Trabalho para Commits

### 1. Antes de Fazer um Commit
- [ ] Execute os testes unitários
- [ ] Verifique se a documentação está atualizada
- [ ] Atualize o CHANGELOG.md se necessário
- [ ] Certifique-se de que as alterações estão cobertas por testes

### 2. Mensagens de Commit
Use o formato convencional de commits:
```
tipo(escopo): descrição curta

Corpo detalhado explicando as mudanças

Refs: #número-da-issue
```

**Tipos de commit:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Formatação, ponto e vírgula, etc. (não altera código)
- `refactor`: Refatoração de código
- `test`: Adição ou modificação de testes
- `chore`: Atualização de tarefas, configurações, etc.

### 3. Atualização de Documentação
- **CHANGELOG.md**: Registre todas as mudanças significativas
- **RELEASES.md**: Atualize com notas de versão acumulativas
- **README.md**: Atualize conforme necessário para refletir novas funcionalidades

### 4. Versionamento
- Siga o [Versionamento Semântico](https://semver.org/)
- Atualize a versão nos arquivos apropriados
- Crie uma tag Git para cada release

## Processo de Code Review
1. Crie um Pull Request (PR) para a branch `main`
2. Adicione revisores relevantes
3. Aguarde a aprovação de pelo menos um revisor
4. Resolva todos os comentários antes de mesclar
5. Atualize a documentação conforme necessário

## Padrões de Código
- Siga as convenções de estilo do Python (PEP 8)
- Documente funções e classes com docstrings
- Mantenha os testes atualizados

## Reportando Problemas
- Verifique se o problema já existe
- Forneça informações detalhadas sobre o ambiente
- Inclua etapas para reproduzir o problema
- Adicione logs e capturas de tela, se aplicável
