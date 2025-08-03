# Gerenciador de Issues do GitHub

Este diretório contém ferramentas para gerenciar todo o ciclo de vida das issues do GitHub de forma automatizada, desde a criação até o fechamento.

## 🌟 Funcionalidades

- **Importação Automática**: Cria issues no GitHub a partir de arquivos JSON e Markdown
- **Suporte a Markdown**: Suporte completo a formatação Markdown nos corpos das issues
- **Metadados Ricos**: Suporte a labels, assignees, milestones e metadados personalizados
- **Rastreamento**: Mantém histórico de todas as issues importadas
- **Seguro**: Armazenamento seguro de tokens de acesso
- **Fluxo de Trabalho**: Suporte a estados de issue (aberto/importado/fechado)

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

## 📋 Fluxo de Trabalho de Issues

### 1. Criando uma Nova Issue

1. Crie dois arquivos no diretório `.github/import_issues/open/`:
   - `NNN-short-description.json` - Arquivo JSON com os metadados da issue
   - `NNN-short-description.md` - Arquivo markdown com a descrição detalhada

2. Execute o script de importação:
   ```bash
   cd .github/import_issues/
   python3 import_issues.py dmirrha/motorsport-calendar
   ```

3. O script irá:
   - Importar a issue para o GitHub
   - Mover os arquivos para `.github/import_issues/imported/`
   - Adicionar um timestamp ao nome dos arquivos

### 2. Após o Pull Request Ser Aceito

1. Mova os arquivos da issue para `.github/import_issues/closed/`:
   ```bash
   mv .github/import_issues/imported/NNN-* .github/import_issues/closed/
   ```

2. Atualize o CHANGELOG.md com as alterações relacionadas à issue.

### 3. Estrutura de Diretórios

- `open/` - Issues a serem processadas
- `imported/` - Issues já importadas para o GitHub (com timestamp)
- `closed/` - Issues que já foram resolvidas e fechadas
- `templates/` - Modelos para novas issues (opcional)

### 4. Convenção de Nomenclatura

- Use números sequenciais com três dígitos (001, 002, ..., 010, 011, etc.)
- Use hífens para separar palavras
- Seja descritivo mas conciso
- Mantenha a consistência entre os nomes dos arquivos .json e .md
- Exemplos:
  - `001-bug-logger-fix.json`
  - `010-feature-new-workflow.json`
  - `100-docs-update-readme.json`

## 🚀 Fluxo de Trabalho Detalhado

### 1. Criando uma Nova Issue

1. **Crie os arquivos necessários** no diretório `.github/import_issues/open/`:
   ```bash
   cp .github/import_issues/templates/issue_template.json open/XXX-short-description.json
   cp .github/import_issues/templates/issue_template.md open/XXX-short-description.md
   ```
   - Substitua `XXX` pelo próximo número sequencial disponível
   - Use nomes descritivos em minúsculas com hífens

2. **Preencha os templates** com as informações da issue:
   - No arquivo `.json`: Defina título, labels, assignees, etc.
   - No arquivo `.md`: Descreva detalhadamente a issue usando Markdown

3. **Execute o script de importação**:
   ```bash
   cd .github/import_issues/
   python3 import_issues.py dmirrha/motorsport-calendar
   ```
   - O script irá solicitar confirmação antes de cada importação
   - Os arquivos serão movidos para a pasta `imported/` com timestamp

### 2. Após a Aprovação do Pull Request

1. **Mova os arquivos** para a pasta `closed/`:
   ```bash
   mv .github/import_issues/imported/XXX-* .github/import_issues/closed/
   ```

2. **Atualize o CHANGELOG.md** com as alterações relacionadas

## 🔧 Pré-requisitos Técnicos

- Python 3.8 ou superior
- Dependências:
  ```bash
  pip install PyGithub cryptography
  ```
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
