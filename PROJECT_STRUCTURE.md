# Estrutura do Projeto - Motorsport Calendar

## **Visão Geral da Arquitetura**

### **Objetivo**
Documentar a arquitetura atual do sistema de geração de calendário de automobilismo, incluindo módulos, responsabilidades e fluxo de dados.

---

## **📁 Estrutura de Diretórios**

```
Race Calendar/
├── motorsport_calendar.py          # Ponto de entrada principal
├── config.json                     # Configuração principal
├── config.example.json             # Exemplo de configuração
├── requirements.txt                # Dependências Python
├── README.md                       # Documentação principal
├── PROJECT_STRUCTURE.md            # Esta documentação
├── DATA_SOURCES.md                 # Documentação das fontes de dados
├── REQUIREMENTS.md                 # Requisitos detalhados
├── .gitignore                      # Configuração do Git
│
├── src/                            # Código fonte modular
│   ├── __init__.py
│   ├── data_collector.py           # Coordena a coleta de dados
│   ├── event_processor.py          # Processa e filtra eventos
│   ├── ical_generator.py           # Gera arquivos iCal
│   ├── config_manager.py           # Gerencia configurações
│   ├── logger.py                   # Sistema de logging
│   ├── ui_manager.py               # Interface do usuário
│   ├── category_detector.py        # Detecta categorias
│   └── utils.py                    # Funções utilitárias
├── 
├── sources/                        # Implementações de fontes
│   ├── __init__.py
│   ├── tomada_tempo.py             # Fonte principal: Tomada de Tempo
│   ├── ergast_api.py               # Integração com Ergast API (F1)
│   ├── motorsport_com.py           # Integração com Motorsport.com
│   └── base_source.py              # Classe base abstrata
├── 
├── output/                         # Saídas geradas
│   └── motorsport_events_YYYYMMDD_HHMMSS.ics  # Arquivo iCal com timestamp
│   └── latest.ics                  # Link simbólico para o mais recente
├── 
├── logs/                           # Sistema de logs
│   ├── debug/                      # Logs detalhados
│   │   ├── YYYY-MM-DD_HH-MM-SS.log # Logs por execução
│   │   └── latest.log              # Último log
│   ├── payloads/                   # Dados brutos
│   │   ├── source_timestamp.json   # Payloads de resposta
│   │   └── processed/              # Dados processados
│   └── app.log                     # Log principal
├── 
└── tests/                          # Testes automatizados
    ├── __init__.py
    ├── unit/                       # Testes unitários
    │   ├── test_data_collector.py
    │   ├── test_event_processor.py
    │   └── test_ical_generator.py
    ├── integration/                # Testes de integração
    │   └── test_sources.py
    └── fixtures/                   # Dados de teste
        └── sample_events.json
```

---

## **🔧 Módulos Principais**

### **1. motorsport_calendar.py** (Script Principal)
- **Função**: Ponto de entrada da aplicação
- **Responsabilidades**:
  - Parsing de argumentos da linha de comando
  - Inicialização do sistema de logs
  - Coordenação dos módulos
  - Tratamento de erros globais

### **2. src/config_manager.py** (Gerenciador de Configuração)
- **Função**: Gerenciamento centralizado de configurações
- **Responsabilidades**:
  - Carregamento e validação do `config.json`
  - Validação de esquema com mensagens claras de erro
  - Fornecimento de valores padrão
  - Suporte a herança de configurações
  - Validação de tipos e valores
  - Criação de configuração inicial se não existir

### **3. src/data_collector.py** (Coletor de Dados)
- **Função**: Orquestração da coleta de eventos
- **Responsabilidades**:
  - Carregamento dinâmico de fontes
  - Execução concorrente segura
  - Timeout e retry automáticos
  - Coleta de métricas de desempenho
  - Cache inteligente de respostas
  - Normalização inicial dos dados

### **4. src/event_processor.py** (Processador de Eventos)
- **Função**: Processamento avançado de eventos
- **Responsabilidades**:
  - Filtragem por data/horário
  - Detecção de eventos recorrentes
  - Consolidação de metadados
  - Aplicação de regras de negócio
  - Geração de IDs únicos
  - Validação de consistência

### **5. src/ical_generator.py** (Gerador iCal)
- **Função**: Geração de calendários no formato iCalendar
- **Responsabilidades**:
  - Serialização de eventos para iCal
  - Suporte a múltiplos fusos horários
  - Geração de UIDs estáveis
  - Inclusão de metadados ricos
  - Suporte a anexos e alertas
  - Otimização de tamanho de arquivo
  - Adição de metadados e lembretes
  - Validação do arquivo gerado

### **6. src/logger.py** (Sistema de Logging Avançado)
- **Função**: Gerenciamento centralizado de logs e payloads
- **Responsabilidades**:
  - Configuração de múltiplos níveis de log
  - Gravação de payloads raw em arquivos separados
  - Rotação automática de logs por execução
  - Formatação e estruturação de logs debug

### **7. src/ui_manager.py** (Interface Visual)
- **Função**: Gerenciamento da interface visual colorida
- **Responsabilidades**:
  - Exibição passo a passo da execução
  - Progress bars e indicadores visuais
  - Formatação colorida de mensagens
  - Ícones e elementos visuais agradáveis

### **8. src/category_detector.py** (Detecção de Categorias)
- **Função**: Identificação e classificação de eventos
- **Responsabilidades**:
  - Análise de texto para identificação
  - Mapeamento de sinônimos
  - Classificação hierárquica
  - Aprendizado de novas categorias
  - Cache de resultados
  - Métricas de confiança
  - Classificação por tipo (carros, motos, outros)
  - Aprendizado e expansão da base de conhecimento
  - Score de confiança para cada categoria detectada

### **9. sources/base_source.py** (Classe Base)
- **Função**: Interface comum para todas as fontes
- **Responsabilidades**:
  - Definição da interface padrão
  - Implementação de funcionalidades comuns
  - Tratamento de erros HTTP
  - Rate limiting e retry logic

---

## **📦 Dependências Principais**

### **Coleta de Dados:**
- `requests` - Requisições HTTP
- `beautifulsoup4` - Parsing HTML
- `lxml` - Parser XML/HTML rápido

### **Processamento de Dados:**
- `python-dateutil` - Manipulação de datas
- `pytz` - Timezones
- `fuzzywuzzy` - Comparação de strings para duplicatas
- `python-levenshtein` - Aceleração para fuzzywuzzy

### **Detecção de Categorias:**
- `nltk` - Processamento de linguagem natural
- `unidecode` - Normalização de caracteres especiais
- `jellyfish` - Algoritmos de similaridade de strings
- `scikit-learn` - Machine learning para classificação (opcional)

### **Geração iCal:**
- `icalendar` - Criação de arquivos iCal
- `uuid` - Geração de IDs únicos

### **Interface Visual e Logging:**
- `rich` - Interface visual rica com cores, progress bars e formatação
- `colorama` - Suporte a cores multiplataforma
- `tqdm` - Progress bars avançadas
- `colorlog` - Logs coloridos estruturados

### **Utilitários:**
- `pyyaml` - Parsing de configurações (opcional)
- `click` - Interface de linha de comando
- `pathlib` - Manipulação de caminhos (built-in Python 3.8+)

---

## **🎯 Arquitetura de Fluxo**

```
1. motorsport_calendar.py
   ↓
2. ui_manager.py (inicializa interface visual)
   ↓
3. config_manager.py (carrega configurações)
   ↓
4. logger.py (configura sistema de logging)
   ↓
5. category_detector.py (inicializa detecção de categorias)
   ↓
6. data_collector.py (coordena coleta)
   ↓
7. sources/*.py (coleta dados + salva payloads)
   ↓
8. category_detector.py (classifica categorias dinamicamente)
   ↓
9. event_processor.py (processa e deduplica)
   ↓
10. ical_generator.py (gera arquivo iCal)
   ↓
11. output/motorsport_events.ics (arquivo final)
```

---

## **⚙️ Configurações de Desenvolvimento**

### **Python Version**
- **Mínimo**: Python 3.8+
- **Recomendado**: Python 3.11+

### **Ambiente Virtual**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### **Execução**
```bash
python motorsport_calendar.py
python motorsport_calendar.py --config custom_config.json
python motorsport_calendar.py --verbose --output custom_output.ics
```

---

**🔍 VALIDAÇÃO NECESSÁRIA:**

1. **A estrutura de pastas está adequada?**
2. **A separação de responsabilidades dos módulos faz sentido?**
3. **Há algum módulo adicional que você gostaria de incluir?**
4. **A arquitetura de fluxo está clara e lógica?**
5. **As dependências listadas atendem às necessidades?**

Confirme se esta estrutura está alinhada com sua visão antes de criarmos os arquivos! 🏁
