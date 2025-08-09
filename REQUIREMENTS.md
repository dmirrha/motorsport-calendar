# Requisitos do Sistema - Motorsport Calendar

> Nota pós-rollback (0.5.1)
>
> A branch `main` foi revertida para o snapshot do commit `9362503` (PR #34). Alguns itens abaixo descrevem funcionalidades que serão reintroduzidas em versões futuras. Consulte `RELEASES.md`.

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
- Sistema avançado de logging com:
  - Códigos de erro estruturados
  - Rastreamento detalhado de operações
  - Rotação e limpeza automática
  - Diferentes níveis de verbosidade
- Gerenciamento de configuração robusto:
  - Validação de esquema
  - Valores padrão sensíveis
  - Documentação embutida
  - Tratamento de erros detalhado
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

### **RF02 - Processamento de Dados**
#### **Implementado** ✅
- Normalização de dados de diferentes fontes
- Validação de eventos coletados
- Filtragem por período de silêncio configurável
- Validação de configuração em tempo de execução
- Processamento em lote com tratamento de erros
- Suporte a operações assíncronas
- Cache inteligente de dados processados semana alvo
- Remoção de duplicatas entre fontes
- Suporte dinâmico a categorias de automobilismo
- Sistema avançado de logging com:
  - Códigos de erro estruturados
  - Rastreamento detalhado de operações

#### **Em Desenvolvimento** 🚧
- Aprimoramento da detecção de categorias
- Expansão para mais fontes de dados
- Suporte a notificações personalizadas

### **RF03 - Gerenciamento de Logs e Dados**
#### **Implementado** ✅
- Sistema de logging unificado
- Rastreamento de operações com IDs únicos
- Armazenamento estruturado de logs
- Rotação e limpeza automática
- Níveis de log configuráveis
- Formatação personalizável
- Suporte a múltiplos destinos (arquivo, console, syslog)

### **RF04 - Geração de Saída**
#### **Implementado** ✅
- Geração de arquivos iCal (.ics)
- Formatação personalizável de eventos
- Suporte a múltiplos formatos de saída
- Validação de esquema de saída
- Tratamento de erros robusto
- Suporte a internacionalização
- Metadados ricos nos eventos
- Links de transmissão incorporados com suporte a múltiplos formatos
- Validação e deduplicação de URLs de streaming
- Configuração flexível via JSON
- Sistema de arquivamento automático de arquivos antigos

## **Requisitos Não-Funcionais**

### **RNF01 - Desempenho**
- Tempo de resposta aceitável (< 2s para operações comuns)
- Baixo consumo de recursos (CPU < 5%, Memória < 100MB)
- Processamento eficiente em lote
- Cache inteligente para operações repetitivas
- Paralelização de tarefas independentes
- Otimização de consultas a fontes remotas
- Compressão de dados em trânsito

### **RNF02 - Segurança**
- Tratamento seguro de credenciais (armazenamento criptografado)
- Validação rigorosa de entrada/saída
- Proteção contra injeção e XSS
- Auditoria de operações sensíveis
- Controle de acesso baseado em funções
- Criptografia de dados em repouso
- Proteção contra vazamento de informações

### **RNF03 - Manutenibilidade**
- Cobertura de testes > 80%
- Documentação técnica abrangente
- Código auto-documentado e padronizado
- Estrutura modular e desacoplada
- Logs detalhados para diagnóstico
- Métricas de qualidade de código
- Integração contínua e entrega contínua

## **Manutenção**

### **Dependências**
- `requests` - Requisições HTTP
- `beautifulsoup4` - Parsing HTML
- `icalendar` - Geração de arquivos .ics
- `python-dateutil` - Manipulação de datas
- `colorama` - Cores no terminal
- `tqdm` - Barras de progresso
- `pydantic` - Validação de dados
- `loguru` - Logging avançado
- `pyyaml` - Suporte a YAML
- `jsonschema` - Validação de JSON Schema
- `pytest` - Framework de testes
- `coverage` - Cobertura de testes
- `mypy` - Checagem estática de tipos
- `black` - Formatação de código

### **Atualizações**
- Verificar regularmente por atualizações de segurança
- Manter documentação atualizada
- Monitorar mudanças nas APIs e sites de origem

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

## **Entregáveis**
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

- pytz (manuseio de timezones)
