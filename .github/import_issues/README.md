# Gerenciador de Issues do GitHub

Este diretório contém ferramentas para gerenciar a importação de issues para o repositório do GitHub de forma automatizada.

## 📋 Histórico de Issues

### ✅ Issues Importadas com Sucesso

1. **🐛 Correção na Detecção de Eventos sem Data**
   - Issue: [#3](https://github.com/dmirrha/motorsport-calendar/issues/3)
   - Arquivo: `imported/20250802_134853_fix_event_detection.json`
   - Status: `imported`

2. **🐛 Correção na Detecção do Final de Semana**
   - Issue: [#5](https://github.com/dmirrha/motorsport-calendar/issues/5)
   - Arquivo: `imported/20250802_134857_fix_weekend_detection.json`
   - Status: `imported`

3. **✨ Aprimoramento na Detecção de Categorias**
   - Issue: [#2](https://github.com/dmirrha/motorsport-calendar/issues/2)
   - Arquivo: `imported/20250802_134852_enhance_category_detection.json`
   - Status: `imported`

4. **🔧 Melhoria no Tratamento de Erros e Logs**
   - Issue: [#4](https://github.com/dmirrha/motorsport-calendar/issues/4)
   - Arquivo: `imported/20250802_134855_improve_error_handling.json`
   - Status: `imported`

### 📝 Como Criar Novas Issues

1. Crie um novo arquivo JSON seguindo o formato abaixo
2. Salve no diretório `.github/import_issues/`
3. Execute o script de importação

## 🚀 Importação Automática de Issues

### Pré-requisitos

- Python 3.6 ou superior
- Biblioteca PyGithub (`pip install PyGithub`)
- Token de acesso pessoal do GitHub com permissão `repo`

### Configuração

1. Crie um token de acesso pessoal no GitHub:
   - Acesse: [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
   - Gere um novo token com a permissão `repo`

2. Configure a variável de ambiente com seu token:
   ```bash
   # Linux/macOS
   export GITHUB_TOKEN='seu_token_aqui'
   
   # Windows (PowerShell)
   $env:GITHUB_TOKEN='seu_token_aqui'
   ```

### Como Usar o Script

1. Navegue até o diretório de importação:
   ```bash
   cd .github/import_issues/
   ```

2. Execute o script de importação:
   ```bash
   python import_issues.py dono/repositorio
   ```
   Exemplo:
   ```bash
   python import_issues.py dmirrha/motorsport-calendar
   ```

3. Siga as instruções na tela para confirmar a importação.

### O que o Script Faz

1. Lista todas as issues disponíveis para importação
2. Solicita confirmação antes de prosseguir
3. Importa cada issue para o repositório especificado
4. Move os arquivos importados para a pasta `imported/`
5. Gera um relatório com o resultado da importação

## 📁 Estrutura de Diretórios

- `imported/` - Issues já importadas (com timestamps)
- `*.json` - Arquivos de issues pendentes
- `import_issues.py` - Script de importação
- `README.md` - Este arquivo

## 🔄 Fluxo de Trabalho

1. Crie novas issues como arquivos JSON neste diretório
2. Use o script para importar as issues para o GitHub
3. Os arquivos importados são movidos automaticamente para `imported/`
4. Mantenha o histórico de issues importadas para referência

## 📝 Estrutura dos Arquivos JSON

Cada arquivo de issue deve seguir este formato:

```json
{
  "title": "Título da Issue",
  "body": "Descrição detalhada em Markdown...",
  "labels": ["bug", "high priority"],
  "assignees": ["usuario"],
  "milestone": null
}
```
