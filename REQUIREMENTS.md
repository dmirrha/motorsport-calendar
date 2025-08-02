# Requisitos do Sistema - Motorsport Calendar

## **Visão Geral**

### **Objetivo do Projeto**
Desenvolver e manter um sistema automatizado para coleta, processamento e exportação de eventos de automobilismo para calendários digitais, com foco em usabilidade e manutenibilidade.

### **Status Atual**
✅ **Versão Estável** - Em produção com suporte a múltiplas fontes de dados e categorias de automobilismo.

## **Requisitos Funcionais**

### **RF01 - Coleta de Dados**
#### **Implementado** ✅
- Coleta automatizada de eventos de múltiplas fontes
- Detecção inteligente do fim de semana alvo
- Remoção de duplicatas entre fontes
- Suporte dinâmico a categorias de automobilismo
- Coleta de metadados ricos incluindo:
  - Nome e descrição do evento
  - Datas e horários com timezone
  - Localização e circuito
  - Categoria detectada automaticamente
  - Links de transmissão quando disponíveis

#### **Em Desenvolvimento** 🚧
- Aprimoramento da detecção de categorias
- Expansão para mais fontes de dados
- Suporte a notificações personalizadas

### **RF02 - Geração de iCal**
#### **Implementado** ✅
- Geração de arquivos .ics compatíveis com RFC 5545
- Suporte a múltiplos fusos horários
- Metadados ricos nos eventos
- Links de transmissão incorporados
- Configuração flexível via JSON

#### **Melhorias Planejadas** 📅
- Suporte a lembretes personalizados
- Opções avançadas de formatação
- Suporte a anexos e documentos relacionados

#### **RF03 - Integração com Google Calendar**
- Arquivo .ics deve ser totalmente compatível com importação no Google Calendar
- Eventos devem aparecer corretamente com todas as informações
- Suporte a atualizações (evitar duplicatas)

## **Requisitos Não-Funcionais**

### **RNF01 - Plataforma**
#### **Suportado** ✅
- **Sistemas Operacionais**: macOS, Linux, Windows
- **Python**: 3.8+
- **Dependências**: Gerenciadas via `requirements.txt`
- **Arquitetura**: Modular e extensível

### **RNF02 - Usabilidade**
#### **Implementado** ✅
- Interface de linha de comando intuitiva
- Saída colorida e formatada
- Barras de progresso em tempo real
- Mensagens de status claras
- Documentação abrangente

#### **Melhorias Planejadas** 📅
- Interface web para configuração
- Dashboard de status
- Notificações por e-mail/telegram

### **RNF03 - Confiabilidade**
#### **Implementado** ✅
- Validação rigorosa de dados
- Mecanismo de fallback para fontes alternativas
- Sistema de logging abrangente:
  - Múltiplos níveis de log (DEBUG, INFO, WARNING, ERROR)
  - Armazenamento de payloads brutos
  - Rotação e retenção configurável
  - Timestamps precisos

#### **Melhorias Planejadas** 📅
- Monitoramento em tempo real
- Alertas automáticos para falhas
- Métricas de desempenho

#### **RNF04 - Manutenibilidade**
- Código bem estruturado e documentado
- **Todas as configurações externalizadas em arquivo de configuração**
- Fácil adição de novas fontes de dados
- Sistema de priorização e exclusão de fontes configurável
- Parâmetros iCal configuráveis sem alteração de código

### **Requerimentos de Dados**

#### **RD01 - Fontes de Dados**
- APIs públicas quando disponíveis
- Web scraping responsável como alternativa
- Múltiplas fontes para redundância
- **Sistema de priorização de fontes configurável**
- **Lista de exclusão de fontes e categorias**
- **Coleta de links de transmissão quando disponíveis**

## **Qualidade dos Dados**

### **Validação**
- **Datas e Horários**:
  - Verificação de fusos horários
  - Detecção de conflitos
  - Validação de formato ISO 8601

- **Consistência**:
  - Verificação de campos obrigatórios
  - Valores padrão para dados opcionais
  - Normalização de textos

### **Processamento**
- **Deduplicação**:
  - Comparação por múltiplos atributos
  - Pontuação de similaridade
  - Manutenção da fonte com maior prioridade

- **Enriquecimento**:
  - Adição de metadados
  - Links para mais informações
  - Dados contextuais

### **Monitoramento**
- Métricas de qualidade
- Alertas para anomalias
- Histórico de mudanças
- Logs de processamento

## **Arquitetura e Configuração**

### **Estrutura do Projeto**
```
motorsport-calendar/
├── config.json               # Configuração principal
├── src/                      # Código fonte
├── sources/                  # Módulos de fontes
├── output/                   # Arquivos gerados
└── logs/                     # Logs e dados brutos
```

### **Arquivo de Configuração (config.json)**
```json
{
  "general": {
    "timezone": "America/Sao_Paulo",
    "log_level": "INFO",
    "output_dir": "./output",
    "ui": {
      "colors_enabled": true,
      "show_progress": true
    }
  },
  "sources": {
    "enabled": ["tomada_tempo", "ergast"],
    "tomada_tempo": {
      "enabled": true,
      "priority": 1,
      "timeout": 30
    },
    "ergast": {
      "enabled": true,
      "priority": 2,
      "timeout": 15
    }
  },
  "ical": {
    "filename": "motorsport_events",
    "timezone": "UTC",
    "reminder_minutes": 15
  }
}
```

## **Roadmap**

### **Próximas Versões**

#### **v1.1 - Melhorias na Detecção**
- Aprimorar detecção automática de categorias
- Adicionar suporte a mais fontes de dados
- Melhorar tratamento de fusos horários

#### **v1.2 - Interface Web**
- Dashboard de configuração
- Visualização de eventos
- Gerenciamento de fontes

#### **v1.3 - Notificações**
- Alertas por e-mail
- Integração com Telegram
- Lembretes personalizados

## **Manutenção**

### **Dependências**
Lista de dependências principais:
- `requests`: Requisições HTTP
- `beautifulsoup4`: Web scraping
- `icalendar`: Geração de arquivos iCal
- `python-dateutil`: Manipulação de datas
- `colorama`: Formatação colorida no terminal

### **Atualizações**
- Verificar regularmente por atualizações de segurança
- Manter documentação atualizada
- Monitorar mudanças nas APIs e sites de origem

#### **Filtros de Eventos**
- **Detecção dinâmica de categorias**: Sistema que identifica automaticamente todas as categorias disponíveis nas fontes
- **Lista de inclusão configurável**: Permite especificar categorias específicas ou usar "*" para todas
- **Lista de exclusão de categorias**: Permite excluir categorias específicas
- **Filtros por país/região**: Configurável por localização
- **Filtros por tipo de evento**: Corrida, treino, classificação, etc.
- **Mapeamento inteligente**: Sistema que reconhece variações de nomes de categorias

## **Filtros e Personalização**

### **Categorias**
- **Inclusão/Exclusão**:
  ```json
  {
    "categories": {
      "include": ["*"],  // Todas as categorias
      "exclude": ["kart"]  // Exceto kart
    }
  }
  ```
- **Mapeamento de Sinônimos**:
  ```json
  {
    "category_mapping": {
      "F1": ["Formula 1", "Fórmula 1", "F1"],
      "MotoGP": ["MotoGP", "Moto GP"]
    }
  }
  ```

### **Filtros Avançados**
- **Por Região**:
  ```json
  {
    "filters": {
      "regions": ["BR", "US"],
      "event_types": ["race", "qualifying"]
    }
  }
  ```

### **Personalização de Saída**
- Formatação de datas
- Idiomas suportados
- Estilos visuais
- Campos personalizados

#### **Parâmetros iCal**
- Nome do calendário
- Descrição do calendário
- Timezone dos eventos
- Duração padrão dos eventos
- Configurações de lembrete (tempo antes do evento)
- Categoria padrão dos eventos
- Prioridade dos eventos
- Status padrão (confirmado, tentativo)

#### **Links de Transmissão**
- Mapeamento de categorias para provedores de streaming
- URLs base para diferentes plataformas
- Configurações regionais para links

#### **Detecção de Fim de Semana e Duplicatas**
- **Algoritmo de fim de semana**: Configuração para identificar o final de semana alvo (sexta a domingo)
- **Critérios de duplicata**: Parâmetros para comparação de eventos (nome, data, horário, categoria)
- **Tolerância de tempo**: Margem de diferença entre horários para considerar como mesmo evento
- **Normalização de nomes**: Regras para padronizar nomes de eventos e categorias
- **Prioridade de fontes**: Ordem de preferência em caso de conflito de dados

#### **Sistema de Logging e Debug**
- **Estrutura de arquivos de log**: Organização por data/execução
- **Payloads raw**: Diretório e formato para armazenamento de respostas das integrações
- **Níveis de log**: Configuração detalhada por módulo
- **Retenção de logs**: Políticas de limpeza automática
- **Formato de saída**: Templates para logs e interface visual

### **Entregáveis**
1. Script Python principal (`motorsport_calendar.py`)
2. **Arquivo de configuração completo (`config.json`)**
3. Lista de dependências (`requirements.txt`)
4. Documentação de uso (`README.md`)
5. Arquivo iCal gerado (`motorsport_events.ics`)
6. **Arquivo de exemplo de configuração (`config.example.json`)**

### **Critérios de Aceitação**

#### **Funcionalidades Básicas**
- [x] Script executa sem erros em macOS, Linux e Windows
- [x] Coleta eventos do final de semana atual
- [x] Gera arquivo .ics válido compatível com RFC 5545
- [x] Arquivo importa corretamente no Google Calendar e outros clientes iCal
- [x] Eventos aparecem com informações completas e formatadas
- [x] Suporte a múltiplos fusos horários

#### **Processamento de Dados**
- [x] Script identifica corretamente o fim de semana alvo
- [x] Duplicatas são removidas mantendo dados da fonte prioritária
- [x] Normalização de dados funciona corretamente
- [ ] **CRÍTICO:** Corrigir detecção da página alvo em tomadadetempo.com.br
  - Identificar corretamente o link alvo da programação
  - Garantir leitura correta dos eventos na página alvo
  - Melhorar resiliência a mudanças na estrutura do site
- [ ] Melhorar detecção de datas em eventos da programação semanal
- [ ] Associar eventos sem data explícita ao contexto da página

#### **Sistema de Logging**
- [x] Interface visual colorida e agradável durante execução
- [x] Payloads raw de todas as integrações são salvos
- [x] Log centralizado debug é gerado a cada execução
- [x] Rotação automática de logs a cada execução
- [x] Limpeza automática de logs antigos baseada em política de retenção
- [x] Configuração flexível de retenção de logs via JSON
- [x] Armazenamento de logs rotacionados em diretório dedicado

#### **Desempenho e Confiabilidade**
- [x] Tratamento de erros robusto
- [x] Timeout configurável para requisições
- [x] Mecanismo de fallback para fontes alternativas

#### **Configuração e Manutenção**
- [x] Todas as configurações em arquivo JSON
- [x] Fácil adição de novas fontes de dados
- [x] Documentação completa e atualizada

---

**VALIDAÇÃO NECESSÁRIA:**
Estes requerimentos estão alinhados com suas expectativas? Há algo que gostaria de adicionar, modificar ou remover antes de prosseguirmos para o próximo passo?
