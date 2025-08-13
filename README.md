# 🏁 Motorsport Calendar Generator

Um script Python avançado para coleta automática de eventos de automobilismo de múltiplas fontes e geração de arquivos iCal para importação no Google Calendar. Desenvolvido para entusiastas de automobilismo que desejam acompanhar todas as corridas do fim de semana em um só lugar.

> Nota pós-rollback (0.5.1)
>
- A branch `main` foi revertida para o snapshot do commit `9362503` (PR #34). Algumas seções abaixo podem descrever funcionalidades que serão reintroduzidas em PRs futuros. O workflow de testes/CI foi reativado via GitHub Actions (`.github/workflows/tests.yml`) em 2025-08-13. Consulte `RELEASES.md` para detalhes.

## 🎯 Características

- ✅ **Coleta automática** de eventos de múltiplas fontes
- ✅ **Interface visual colorida** com progresso em tempo real
- ✅ **Detecção inteligente** do fim de semana alvo
- ✅ **Remoção de duplicatas** entre fontes
- ✅ **Configuração flexível** via arquivo JSON
- ✅ **Logging avançado** com rotação e limpeza automática
- ✅ **Links de transmissão** incluídos nos eventos do calendário
- ✅ **Arquivamento automático** de arquivos iCal antigos
- ✅ **Períodos de silêncio** configuráveis para filtrar eventos por horário

## Categorias Suportadas

**Suporte Dinâmico a TODAS as Categorias de Esporte Automotor**

O script detecta automaticamente e coleta eventos de **qualquer categoria** encontrada nas fontes de dados, incluindo mas não limitado a:

### Carros:
### **🏎️ Carros:**
- Fórmula 1, F2, F3, F4
- Stock Car Brasil, NASCAR
- IndyCar, Super Fórmula
- WEC (World Endurance Championship)
- IMSA, DTM, Super GT
- Fórmula E, Extreme E
- Rally (WRC), Rallycross
- Turismo, GT World Challenge

### **🏍️ Motos:**
- MotoGP, Moto2, Moto3
- World Superbike (WSBK)
- Supersport, Superstock
- MotoE, MotoAmerica
- British Superbike (BSB)

### **🚗 Outras Modalidades:**
- Karting, Drift
- Arrancada, Autocross
- Hill Climb, Time Attack
- **E muito mais!**

> 💡 **Flexibilidade Total:** O sistema se adapta automaticamente a novas categorias que apareçam nas fontes de dados, sem necessidade de atualizações no código.

## 🔇 Períodos de Silêncio

Os períodos de silêncio permitem configurar intervalos de tempo durante os quais os eventos não serão incluídos no arquivo iCal de saída, mas ainda serão exibidos nos logs para fins de monitoramento.

### Configuração

Adicione a seção `silent_periods` no arquivo de configuração:

```json
{
  "general": {
    "silent_periods": [
      {
        "enabled": true,
        "name": "Noite",
        "start_time": "22:00",
        "end_time": "06:00",
        "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "sunday"]
      },
      {
        "enabled": true,
        "name": "Fim de Semana",
        "start_time": "00:00",
        "end_time": "23:59",
        "days_of_week": ["saturday", "sunday"]
      }
    ]
  }
}
```

### Parâmetros

- **`enabled`**: Ativa ou desativa o período de silêncio
- **`name`**: Nome descritivo do período
- **`start_time`**: Horário de início no formato HH:MM
- **`end_time`**: Horário de fim no formato HH:MM
- **`days_of_week`**: Lista de dias da semana (monday, tuesday, etc.)

### Comportamento

- Eventos que ocorrem durante períodos de silêncio são **filtrados** do arquivo iCal
- Os eventos filtrados são **registrados nos logs** com nível INFO
- Um **resumo dos eventos filtrados** é exibido na saída do terminal
- O sistema lida corretamente com períodos que **cruzam a meia-noite**

### Exemplo de Uso

```bash
# Executar com períodos de silêncio configurados
python3 motorsport_calendar.py --verbose
```

Os logs mostrarão:
```
🔇 Event filtered by silent period 'Noite': F1 Practice at 2025-08-03 23:30
🔇 Silent periods filtered 3 events:
  • Noite: 2 events
  • Fim de Semana: 1 events
```

## 👥 Como Contribuir

Agradecemos seu interesse em contribuir para o Motorsport Calendar! Aqui está como você pode ajudar:

### 📝 Reportando Problemas

1. **Verifique se já existe uma issue** relacionada ao problema
2. Se não existir, cite uma nova issue seguindo nosso modelo
3. Use o template apropriado (bug report ou feature request)
4. Inclua informações detalhadas para reproduzir o problema

### 🛠️ Fluxo de Trabalho para Issues

#### 1. Criando uma Nova Issue

1. **Crie os arquivos necessários** no diretório `.github/import_issues/open/`:
   ```bash
   # Usando os templates
   cp .github/import_issues/templates/issue_template.json open/NNN-descricao-curta.json
   cp .github/import_issues/templates/issue_template.md open/NNN-descricao-curta.md
   ```
   - `NNN` deve ser o próximo número sequencial disponível (ex: 001, 002, etc.)
   - Use nomes descritivos em minúsculas com hífens

2. **Preencha os templates** com as informações da issue:
   - No arquivo `.json`: Defina título, labels, assignees, etc.
   - No arquivo `.md`: Descreva detalhadamente a issue usando Markdown

#### 2. Importando a Issue para o GitHub

1. **Execute o script de importação**:
   ```bash
   cd .github/import_issues/
   python3 import_issues.py dmirrha/motorsport-calendar
   ```
   - O script irá solicitar confirmação antes de cada importação
   - Os arquivos serão movidos para a pasta `imported/` com timestamp
   - Um link para a issue será exibido após a importação

2. **Verifique a issue** no GitHub para garantir que foi criada corretamente

#### 3. Após a Aprovação do Pull Request

1. **Mova os arquivos** para a pasta `closed/`:
   ```bash
   mv .github/import_issues/imported/NNN-* .github/import_issues/closed/
   ```
   - Isso mantém o histórico organizado e evita duplicação

2. **Atualize o CHANGELOG.md** com as alterações relacionadas
   - Inclua uma breve descrição da correção ou melhoria
   - Referencie o número da issue (ex: `#123`)

#### 4. Boas Práticas

- **Nomenclatura de Arquivos**:
  - Use sempre 3 dígitos (ex: `001-`, `010-`, `100-`)
  - Mantenha consistência entre os nomes dos arquivos .json e .md
  - Exemplos: 
    - `001-bug-logger-fix.json`
    - `010-feature-new-workflow.json`

- **Conteúdo das Issues**:
  - Seja claro e objetivo no título
  - Inclua todos os detalhes necessários para reproduzir o problema
  - Adicione screenshots ou exemplos quando relevante
  - Use formatação Markdown para melhor legibilidade

- **Fluxo de Trabalho**:
  - Sempre crie a issue antes de começar a trabalhar nela
  - Use branches descritivas baseadas no número da issue
  - Referencie a issue nos commits (ex: `fix: corrige problema #123`)

### 🏗️ Desenvolvendo Novas Funcionalidades

1. Crie uma branch a partir de `main`
   ```bash
   git checkout -b feature/nome-da-feature
   ```

2. Faça commit das suas alterações
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   ```

3. Envie as alterações
   ```bash
   git push origin feature/nome-da-feature
   ```

4. Abra um Pull Request
   - Descreva as alterações propostas
   - Referencie as issues relacionadas
   - Atualize a documentação conforme necessário

### 📚 Padrões de Código

- Siga o estilo de código existente
- Inclua testes para novas funcionalidades
- Atualize a documentação relevante
- Mantenha os commits atômicos e bem descritos

## 🧪 Testes

- Execução local:
  ```bash
  pytest -q
  ```
- Fixtures essenciais (determinismo/isolamento):
  - `freeze_datetime`: congela `datetime.now()`/`today()` nos módulos relevantes.
  - `fixed_uuid`: força `uuid.uuid4()` a retornar UUID fixo.
  - Fakes de HTTP: `_DummyResponse`/`_DummySession` com `patch_requests_get`/`patch_requests_session` (sem rede real).
- Dados de teste: `tests/data/` com exemplos mínimos (ver `tests/data/README.md`).
- Guia completo: consulte `tests/README.md` para exemplos e boas práticas.

## 🔧 Requisitos

- **Python 3.8+**
- **Sistema Operacional**: macOS, Linux, Windows (testado principalmente no macOS)
- **Conexão com internet** para coleta de dados
- **Dependências**: Verifique o arquivo `requirements.txt` para a lista completa

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/motorsport-calendar.git
cd motorsport-calendar

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o arquivo de configuração
mkdir -p config
cp config/config.example.json config/config.json
# Edite config/config.json conforme necessário
```

## 🧪 Testes

A suíte utiliza Pytest com cobertura via pytest-cov. O gate de cobertura global está configurado em **45%**.

- Gate atual: `--cov-fail-under=45` (definido em `pytest.ini`)
- Mocks essenciais:
  - Timezone fixo `America/Sao_Paulo` e aleatoriedade determinística (`random.seed(0)`)
  - Shims de rede: `sources.tomada_tempo.requests.get` e `sources.base_source.requests.Session`
  - Isolamento de filesystem via `tmp_path`/`tmp_path_factory`
  - Variáveis de ambiente com `monkeypatch.setenv`/`delenv`
- Como rodar: consulte `tests/README.md` para comandos, estrutura e exemplos.

### Fase 2 — Testes Integrados (Governança)

- Épico: #78 — Testes Integrados e Validação de ICS
- Sub-issues: #79–#86
- Documentação sincronizada: `docs/TEST_AUTOMATION_PLAN.md`, `CHANGELOG.md`, `RELEASES.md`
- Rastreabilidade: `docs/issues/open/issue-{78..86}.{md,json}`
 - PR: #87 (https://github.com/dmirrha/motorsport-calendar/pull/87)

Comandos rápidos (local):

```bash
# Suíte completa com cobertura e relatórios
pytest --cov=src --cov=sources \
  --cov-report=term-missing:skip-covered \
  --cov-report=xml:coverage.xml --cov-report=html \
  -q --junitxml=test_results/junit.xml

# Foco em módulos críticos
pytest -q tests/unit/utils/test_payload_manager*.py
pytest -q tests/unit/ical/test_ical_generator*.py

# Checagem de estabilidade (zero flakes)
for i in 1 2 3; do pytest -q; done
```

Cobertura e métricas recentes (Fase 1.1 — issue #59):
- `sources/tomada_tempo.py`: 63%
- Suíte: 101 passed; cobertura global: 40.64%

> Nota: o bug de precedência ISO vs BR em `_extract_date()` foi documentado para importação em lote ao final da Fase 1.1; arquivos no importador: `.github/import_issues/open/025-tomadatemposource-extract-date-parsing-precedence.{json,md}`.

Cobertura e métricas recentes (Fase 1.1 — issue #62):
- `src/ical_generator.py`: **76%**
- Suíte: **156 passed**; cobertura global: **51.92%**
- Novos testes: `tests/unit/ical/test_ical_generator_extended.py`
- Nota: corrigido efeito colateral de monkeypatch global em `pytz.timezone` nos testes de processamento para não interferir nos testes de iCal

Cobertura e métricas recentes (Fase 1.1 — issue #63):
- Suíte: **170 passed**; cobertura global: **57.86%**
- Gate global: `--cov-fail-under=45`
- Novos testes: `tests/unit/category/test_category_detector_basic.py`, `tests/unit/utils/test_payload_manager_extended.py`, `tests/unit/config/test_config_manager_basic.py`

Cobertura e métricas recentes (Fase 1.1 — issue #64):
- Suíte: **205 passed**; cobertura global: **61.52%**
- `src/utils/payload_manager.py`: **90%**
- `src/ical_generator.py`: **93%**
- Novos testes: `tests/unit/utils/test_payload_manager_errors.py`, `tests/unit/ical/test_ical_generator_branches.py`
- Ajustes: construtor de `ICalGenerator` aceita `config_manager` (no teste) e exceção encapsulada em `PayloadManager.save_payload` validada como `IOError`

## 🚀 Uso

```bash
# Execução básica
python motorsport_calendar.py

# Com configuração personalizada
python motorsport_calendar.py --config custom_config.json

# Com saída personalizada
python motorsport_calendar.py --output meu_calendario.ics

# Modo verbose
python motorsport_calendar.py --verbose
```

## 📁 Estrutura do Projeto

```
motorsport-calendar/
├── .github/
│   └── import_issues/        # Gerenciamento de issues
│       ├── imported/         # Issues já importadas
│       ├── *.json            # Issues pendentes
│       ├── import_issues.py  # Script de importação
│       └── README.md         # Documentação
├── motorsport_calendar.py    # Script principal
├── config/                   # Configurações
│   ├── config.json           # Configuração principal
│   └── config.example.json   # Exemplo de configuração
├── requirements.txt          # Dependências
├── src/                      # Código fonte modular
├── sources/                  # Módulos de coleta por fonte
├── output/                   # Arquivos iCal gerados
├── logs/                     # Logs e payloads
└── tests/                    # Testes unitários
```

## ⚙️ Configuração

O arquivo `config/config.json` permite personalizar. Consulte o [Guia de Configuração](docs/CONFIGURATION_GUIDE.md) para uma referência detalhada de todas as opções disponíveis.

- **Fontes de dados** e prioridades
- **Categorias** incluídas/excluídas
- **Parâmetros iCal** (timezone, lembretes, etc.)
- **Links de transmissão** por região
- **Sistema de logging**

## 🎨 Interface Visual

O script exibe uma interface colorida com:
- Progress bars em tempo real
- Status de cada fonte de dados
- Contadores de eventos coletados
- Indicadores visuais de sucesso/erro

## 📊 Logging e Debug

O sistema de logs avançado oferece monitoramento detalhado e solução de problemas:

- **Logs centralizados** com múltiplos níveis (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Payloads raw** preservados por fonte para análise detalhada
## 📊 Logging Avançado

O sistema de logging foi aprimorado com recursos profissionais para facilitar a depuração e monitoramento:

### 🎯 Recursos Principais

- **Mensagens de Erro Estruturadas**
  - Códigos de erro únicos para cada tipo de problema
  - Mensagens claras e acionáveis
  - Sugestões de correção baseadas no contexto

- **Rotação Automática**
  - O arquivo principal de log é rotacionado a cada execução
  - Logs antigos são armazenados em `logs/rotated_logs/`
  - Níveis de log configuráveis por saída (console/arquivo)
  - Formatação personalizável para diferentes destinos

- **Limpeza Inteligente**
  - Remoção automática de logs antigos baseada em idade e quantidade
  - Limpeza seletiva por tipo de log (debug, payloads, etc.)
  - Configuração flexível de retenção

### ⚙️ Configuração de Logging

No arquivo `config.json`, você pode personalizar o comportamento do logging:

```json
"logging": {
  "file_structure": {
    "main_log": "logs/app.log",
    "debug_directory": "logs/debug",
    "payload_directory": "logs/payloads"
  },
  "retention": {
    "enabled": true,
    "max_logs_to_keep": 10,
    "max_payloads_to_keep": 20,
    "delete_older_than_days": 30
  },
  "levels": {
    "console": "INFO",
    "file": "DEBUG",
    "debug_file": "DEBUG"
  },
  "format": {
    "console": "%(message)s",
    "file": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
  },
  "rotation": {
    "enabled": true,
    "max_size_mb": 10,
    "backup_count": 5
  },
  "payload_settings": {
    "save_raw": true,
    "pretty_print": true,
    "include_headers": true,
    "separate_by_source": true,
    "max_files_per_source": 50,
    "max_age_days": 30
  }
}
```

### 🔍 Códigos de Erro

O sistema utiliza códigos de erro estruturados para facilitar a identificação de problemas:

- **1xx**: Erros de Configuração
  - `100`: Configuração ausente
  - `101`: Configuração inválida
  - `102`: Erro de validação

- **2xx**: Erros de Rede
  - `200`: Falha na requisição HTTP
  - `201**: Timeout de conexão
  - `202`: Erro de autenticação

- **3xx**: Erros de Processamento
  - `300`: Falha no processamento de dados
  - `301`: Formato de dados inválido
  - `302`: Falha na normalização

### 📦 Gerenciamento de Payloads

O sistema agora gerencia automaticamente os arquivos de payload:

- **Rotação por quantidade**
  - Mantém apenas os N arquivos mais recentes por fonte
  - Configurável via `max_files_per_source`
  - Remove automaticamente os arquivos mais antigos

- **Limpeza por idade**
  - Remove arquivos mais antigos que X dias
  - Configurável via `max_age_days`
  - Aplicável a logs e payloads

- **Organização**
  - Separação por fonte de dados
  - Nomenclatura consistente de arquivos
  - Metadados incluídos nos nomes dos arquivos

### 🛠️ Validação de Configuração

A validação de configuração foi aprimorada com:

- Verificação de tipos e valores
- Valores padrão sensatos
- Mensagens de erro detalhadas
- Sugestões de correção
- Validação de caminhos e permissões

### 🔄 Períodos de Silêncio

Configure períodos de silêncio para reduzir notificações em horários específicos:

```json
"silent_periods": [
  {
    "name": "Noite",
    "start_time": "22:00",
    "end_time": "07:00",
    "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "sunday"],
    "enabled": true
  },
  {
    "name": "Fim de Semana",
    "start_time": "00:00",
    "end_time": "08:00",
    "days_of_week": ["friday", "saturday", "sunday"],
    "enabled": true
  }
]
```
  - Mantém apenas os logs mais recentes (configurável)
  - Remove automaticamente logs mais antigos que o período de retenção
  - Configuração flexível de retenção
- **Debug completo** para troubleshooting com informações detalhadas

📘 **Documentação Detalhada:** Consulte [LOGGING_AND_CONFIGURATION.md](docs/LOGGING_AND_CONFIGURATION.md) para informações completas sobre configuração e personalização do sistema de logs.

## 🌐 Fontes de Dados

### Fonte Primária
- **Tomada de Tempo** (tomadadetempo.com.br) - Prioridade máxima
  - Coleta detalhada de programação de TV e internet
  - Suporte a múltiplas categorias de automobilismo
  - Atualização em tempo real dos horários de transmissão

### Fontes Secundárias
- **Ergast API** (http://ergast.com/mrd/) - Dados históricos e atuais de F1
- **OpenF1 API** (https://openf1.org/) - Alternativa moderna para dados de F1
- **Sites oficiais** das categorias - Para informações diretas das fontes oficiais
- **Motorsport.com** - Cobertura abrangente de múltiplas categorias
- **Autosport** - Dados confiáveis sobre automobilismo mundial

> ⚠️ **Nota sobre a Ergast API**: Será descontinuada em 2024. O sistema já está preparado para a transição para a OpenF1 API.

## 📅 Importação no Google Calendar

1. Execute o script para gerar o arquivo .ics
2. Abra o Google Calendar
3. Clique em "+" ao lado de "Outros calendários"
4. Selecione "Importar"
5. Faça upload do arquivo motorsport_events.ics

## 🐛 Gerenciamento de Issues

O projeto utiliza um sistema automatizado para gerenciar issues através de arquivos JSON. Isso permite:

- ✅ **Rastreabilidade**: Histórico completo de todas as issues
- ✅ **Consistência**: Formato padronizado para todas as issues
- ✅ **Automação**: Processo de importação simplificado
- ✅ **Backup**: Histórico de todas as issues já criadas

### 🔍 Issues Ativas

1. [🐛 Correção na Detecção de Eventos sem Data](https://github.com/dmirrha/motorsport-calendar/issues/3)
2. [🐛 Correção na Detecção do Final de Semana](https://github.com/dmirrha/motorsport-calendar/issues/5)
3. [✨ Aprimoramento na Detecção de Categorias](https://github.com/dmirrha/motorsport-calendar/issues/2)
4. [🔧 Melhoria no Tratamento de Erros e Logs](https://github.com/dmirrha/motorsport-calendar/issues/4)

### ✅ Issues Concluídas

- [#49 — Prioritários Fase 1](https://github.com/dmirrha/motorsport-calendar/issues/49) — PR #56 mergeada; issue fechada automaticamente. Rastreabilidade: `docs/issues/closed/issue-49.md`.
- [#64 — Backlog Prioritário de Cobertura ≥80% (P1–P6)](https://github.com/dmirrha/motorsport-calendar/issues/64) — concluída com suíte estável 3× e documentação sincronizada; PR #73 atualizada.

### 🔄 Fluxo de Trabalho

1. **Criar Nova Issue**:
   - Crie um novo arquivo JSON em `.github/import_issues/`
   - Siga o [formato padrão](#-formato-do-arquivo-de-issue)

2. **Importar Issues**:
   ```bash
   # Navegue até o diretório de importação
   cd .github/import_issues/
   
   # Execute o script (ele pedirá autenticação na primeira vez)
   python import_issues.py dmirrha/motorsport-calendar
   ```

3. **Verificação**:
   - As issues importadas são movidas para `imported/` com timestamp
   - Um relatório detalhado é exibido no terminal
   - Links para as issues criadas são fornecidos

### 📝 Formato do Arquivo de Issue

```json
{
  "title": "Título da Issue",
  "body": "Descrição detalhada em Markdown...",
  "labels": ["bug", "high priority"],
  "assignees": ["usuario"],
  "milestone": null
}
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🧪 Testes

Execute os testes com Pytest (cobertura habilitada por padrão via `pytest.ini`).

### Instalação das dependências de desenvolvimento

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Comandos principais

```bash
# Testes unitários com cobertura e relatórios (padrão)
pytest

# Apenas testes marcados como unit
pytest -m unit

# Abrir relatório HTML de cobertura após a execução
open htmlcov/index.html  # macOS

# Saídas configuradas
# - Cobertura XML: coverage.xml
# - Cobertura HTML: htmlcov/
# - JUnit XML: test_results/junit.xml
```

Notas:
- Gate de cobertura global: 45% (`--cov-fail-under=45`).
 - Timezone padrão dos testes: `America/Sao_Paulo` (fixture autouse em `tests/conftest.py`).
 - Mocks essenciais documentados em `tests/README.md`:
  - TZ e aleatoriedade fixas (fixtures autouse em `tests/conftest.py`).
  - Rede com shims/patches (`patch_requests_get`, `patch_requests_session`).
  - Isolamento de filesystem com `tmp_path`.
  - Variáveis de ambiente com `monkeypatch.setenv`/`delenv`.
- Exemplos-práticos:
  - `tests/unit/utils/test_payload_manager.py`
  - `tests/unit/test_env_vars.py`
  - `tests/unit/sources/base_source/test_make_request.py`
  - `tests/unit/sources/tomada_tempo/test_parse_calendar_page.py`

Para detalhes, veja `tests/README.md`.

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🏁 Status do Projeto

🚀 **Versão Estável** - Em produção

### 🚀 Últimas Atualizações

#### Sistema de Logging Avançado
- 🔄 **Rotação automática** de logs a cada execução
- 🗑️ **Limpeza inteligente** de logs antigos baseada em política de retenção
- 📊 **Armazenamento organizado** de logs rotacionados
- ⚙️ **Configuração flexível** via arquivo JSON

#### Melhorias no Processamento
- 🔍 Detecção aprimorada de eventos do Tomada de Tempo
- 🕒 Processamento mais preciso de datas e horários
- 🛠️ Tratamento de erros aprimorado
- ⚡ Otimização de performance

#### Próximos Passos Imediatos
- 🐛 **Correção crítica**: Melhorar detecção da página alvo no Tomada de Tempo
- 📅 Aprimorar associação de eventos sem data explícita
- 🔄 Expansão para mais fontes de dados

### Próximos Passos
- Implementação de mais fontes de dados
- Melhorias na detecção de categorias
- Suporte a notificações personalizadas
- Interface web para configuração e visualização
- Exportação para outros formatos de calendário

---

**Desenvolvido com ❤️ para entusiastas do automobilismo**
