# 📚 Documentação do Novo Workflow de Gestão de Issues

## 🎯 Objetivo
Documentar as melhorias implementadas no workflow de gestão de issues do projeto, garantindo que todos os contribuidores possam utilizá-lo de forma eficiente.

## ✨ Melhorias Implementadas

### 1. Estrutura de Diretórios
```
.github/import_issues/
├── open/           # Issues a serem processadas
├── imported/       # Issues já importadas (com timestamp)
├── closed/         # Issues resolvidas e fechadas
└── templates/      # Modelos para novas issues
```

### 2. Script de Importação
- Busca automática de arquivos no diretório `open/`
- Suporte a arquivos Markdown como corpo das issues
- Tratamento de erros aprimorado
- Movimentação automática de arquivos processados

### 3. Templates Padronizados
- `issue_template.json` - Metadados da issue
- `issue_template.md` - Descrição detalhada
- Fluxo de trabalho documentado

## 📋 Como Usar

### Criar Nova Issue
1. Crie os arquivos no diretório `open/`:
   ```bash
   cp templates/issue_template.json open/NNN-descricao.json
   cp templates/issue_template.md open/NNN-descricao.md
   ```
2. Preencha os arquivos conforme necessário
3. Execute o script de importação:
   ```bash
   cd .github/import_issues/
   python3 import_issues.py dmirrha/motorsport-calendar
   ```

### Após o Merge do PR
1. Mova os arquivos para `closed/`:
   ```bash
   mv imported/NNN-* closed/
   ```
2. Atualize o CHANGELOG.md

## 🔍 Issues Relacionadas
- #14 - Melhorar o workflow de gerenciamento de issues
- #16 - Teste: Importação de Markdown

## 📅 Próximos Passos
- [ ] Revisar e aprovar esta documentação
- [ ] Atualizar o guia do contribuidor
- [ ] Realizar treinamento com a equipe

## 📚 Recursos
- [Documentação Completa](.github/import_issues/README.md)
- [Modelos de Issue](.github/import_issues/templates/)
- [Exemplo de Uso](#)
