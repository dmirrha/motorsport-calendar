# ✨ Melhorar o workflow de gerenciamento de issues

## 📝 Descrição
Este PR implementa melhorias significativas no workflow de gerenciamento de issues do projeto, tornando-o mais organizado, automatizado e fácil de usar.

## 🔍 Contexto
O fluxo anterior de gerenciamento de issues estava fragmentado entre múltiplos diretórios e faltava documentação clara, o que poderia levar a inconsistências e dificuldades na manutenção.

## 🎯 Melhorias Implementadas

### Estrutura de Diretórios
- Criada estrutura unificada em `.github/import_issues/`
  - `open/` - Novas issues a serem processadas
  - `imported/` - Issues já importadas para o GitHub
  - `closed/` - Issues resolvidas e fechadas
  - `templates/` - Modelos para novas issues

### Script de Importação Aprimorado
- Busca automática de arquivos no diretório `open/`
- Tratamento de erros aprimorado
- Movimentação automática de arquivos para `imported/`
- Suporte a arquivos Markdown e JSON

### Documentação
- Adicionada seção "Como Contribuir" no README principal
- Documentação detalhada em `.github/import_issues/README.md`
- Modelos de issue padronizados

## 📊 Impacto
**Alto** - Esta mudança afeta todos os contribuidores do projeto, tornando o processo de criação e gerenciamento de issues mais eficiente e padronizado.

## ✅ Critérios de Aceitação
- [x] Estrutura de diretórios criada
- [x] Script de importação atualizado
- [x] Documentação completa no README
- [x] Modelos de issue criados
- [x] Issues existentes migradas para a nova estrutura

## 📚 Recursos Adicionais
- [Guia de Contribuição](.github/import_issues/README.md)
- [Modelo de Issue](.github/import_issues/templates/issue_template.md)

## 📋 Tarefas
- [x] Criar estrutura de diretórios
- [x] Atualizar script de importação
- [x] Criar templates
- [x] Atualizar documentação
- [ ] Revisar e aprovar as mudanças
- [ ] Mesclar para a branch principal
