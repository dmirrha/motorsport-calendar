# Estrutura do Projeto - Motorsport Calendar

## **Passo 2.1: Estrutura Básica do Projeto**

### **Objetivo**
Definir a arquitetura de pastas, módulos principais e organização do código para o script de calendário de automobilismo.

---

## **📁 Estrutura de Diretórios**

```
Race Calendar/
├── motorsport_calendar.py          # Script principal executável
├── config.json                     # Arquivo de configuração principal
├── config.example.json             # Exemplo de configuração
├── requirements.txt                # Dependências Python
├── README.md                       # Documentação de uso
├── .gitignore                      # Arquivos ignorados pelo Git
├── 
├── src/                            # Código fonte modular
│   ├── __init__.py
│   ├── data_collector.py           # Módulo de coleta de dados
│   ├── event_processor.py          # Processamento e deduplicação
│   ├── ical_generator.py           # Geração de arquivos iCal
│   ├── config_manager.py           # Gerenciamento de configurações
│   ├── logger.py                   # Sistema de logging avançado
│   ├── ui_manager.py               # Interface visual colorida
│   └── utils.py                    # Utilitários e helpers
├── 
├── sources/                        # Módulos específicos por fonte
│   ├── __init__.py
│   ├── tomada_tempo.py             # Scraper para Tomada de Tempo
│   ├── ergast_api.py               # Cliente para Ergast API
│   ├── motorsport_com.py           # Scraper para Motorsport.com
│   └── base_source.py              # Classe base para fontes
├── 
├── output/                         # Arquivos gerados
│   └── motorsport_events.ics       # Arquivo iCal gerado
├── 
├── logs/                           # Logs de execução
│   ├── debug/                      # Logs debug detalhados por execução
│   │   ├── 2024-08-01_16-30-15.log # Log debug com timestamp
│   │   └── latest.log              # Symlink para último log
│   ├── payloads/                   # Payloads raw das integrações
│   │   ├── tomada_tempo_20240801.json
│   │   ├── ergast_api_20240801.json
│   │   └── motorsport_com_20240801.json
│   └── motorsport_calendar.log     # Log principal
├── 
└── tests/                          # Testes unitários
    ├── __init__.py
    ├── test_data_collector.py
    ├── test_event_processor.py
    ├── test_ical_generator.py
    └── test_sources.py
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
- **Função**: Carregamento e validação das configurações
- **Responsabilidades**:
  - Leitura do arquivo config.json
  - Validação de configurações obrigatórias
  - Merge com configurações padrão
  - Acesso thread-safe às configurações

### **3. src/data_collector.py** (Coletor de Dados)
- **Função**: Coordenação da coleta de dados
- **Responsabilidades**:
  - Instanciação das fontes de dados
  - Execução paralela das coletas
  - Agregação dos resultados
  - Tratamento de falhas por fonte

### **4. src/event_processor.py** (Processador de Eventos)
- **Função**: Processamento e limpeza dos dados
- **Responsabilidades**:
  - Detecção automática do fim de semana
  - Normalização de dados
  - Detecção e remoção de duplicatas
  - Validação de dados coletados

### **5. src/ical_generator.py** (Gerador iCal)
- **Função**: Criação do arquivo iCal
- **Responsabilidades**:
  - Conversão de eventos para formato iCal
  - Aplicação de configurações de calendário
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

### **8. sources/base_source.py** (Classe Base)
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
5. data_collector.py (coordena coleta)
   ↓
6. sources/*.py (coleta dados + salva payloads)
   ↓
7. event_processor.py (processa e deduplica)
   ↓
8. ical_generator.py (gera arquivo iCal)
   ↓
9. output/motorsport_events.ics (arquivo final)
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
