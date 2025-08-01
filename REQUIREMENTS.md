# Requerimentos Gerais - Script de Calendário de Automobilismo

## **Passo 1.0: Descrição dos Requerimentos Gerais**

### **Objetivo do Projeto**
Desenvolver um script Python que automatize a coleta de informações sobre eventos de automobilismo (carros e motos) que acontecerão no final de semana e gere um arquivo iCal (.ics) para importação no Google Calendar.

### **Requerimentos Funcionais**

#### **RF01 - Coleta de Dados**
- O script deve coletar informações de eventos de automobilismo programados para o final de semana alvo
- **Detecção automática do fim de semana**: O script deve identificar o final de semana alvo a partir da primeira data de evento encontrada nas fontes
- **Remoção de duplicatas**: O script deve ser capaz de identificar e remover eventos duplicados encontrados em diferentes fontes
- **Suporte dinâmico a categorias**: O script deve detectar e coletar eventos de QUALQUER categoria de esporte automotor encontrada nas fontes de dados
- **Extensibilidade automática**: Novas categorias devem ser automaticamente suportadas sem modificação de código
- Informações coletadas devem incluir:
  - Nome do evento/corrida
  - Data e horário
  - Local/circuito
  - Categoria (F1, MotoGP, etc.)
  - Descrição adicional (se disponível)

#### **RF02 - Geração de iCal**
- Gerar arquivo .ics compatível com padrão iCalendar (RFC 5545)
- Incluir timezone correto (configurável via arquivo de configuração)
- Adicionar metadados apropriados (título, descrição, localização)
- Suporte a lembretes/alertas configuráveis
- Parâmetros do evento iCal totalmente configuráveis (duração, categoria, prioridade, etc.)
- Descrição do evento deve incluir link direto para transmissão quando disponível

#### **RF03 - Integração com Google Calendar**
- Arquivo .ics deve ser totalmente compatível com importação no Google Calendar
- Eventos devem aparecer corretamente com todas as informações
- Suporte a atualizações (evitar duplicatas)

### **Requerimentos Não-Funcionais**

#### **RNF01 - Plataforma**
- Executável em macOS (MacBook)
- Python 3.8+ compatível
- Dependências mínimas e bem documentadas

#### **RNF02 - Usabilidade**
- Script simples de executar via linha de comando
- **Interface visual colorida**: Exibição passo a passo da execução com cores e elementos visuais agradáveis
- **Progresso em tempo real**: Indicadores visuais de progresso para cada etapa
- Mensagens de log claras e informativas
- Tratamento de erros robusto

#### **RNF03 - Confiabilidade**
- Validação de dados coletados
- Fallback em caso de falha de uma fonte de dados
- **Sistema de logging avançado**:
  - Log centralizado em modo debug para toda execução
  - Gravação de payloads raw de todas as integrações em arquivos separados
  - Logs detalhados com timestamps e níveis de severidade
  - Rotação automática de logs por execução

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

#### **RD02 - Qualidade dos Dados**
- Validação de formato de datas/horários
- Verificação de consistência das informações
- Tratamento de dados faltantes ou incorretos
- **Algoritmo de detecção de duplicatas**: Comparação por nome do evento, data, horário e categoria
- **Priorização de fontes**: Em caso de duplicatas, manter dados da fonte com maior prioridade
- **Normalização de dados**: Padronização de nomes de eventos e categorias para facilitar detecção de duplicatas

### **Estrutura do Arquivo de Configuração**

O arquivo `config.json` deve conter as seguintes seções:

#### **Configurações Gerais**
- Timezone padrão
- Idioma das mensagens
- Nível de log (DEBUG, INFO, WARNING, ERROR)
- Diretório de saída
- **Configurações de interface visual** (cores, ícones, progress bars)
- **Configurações de logging avançado** (formato, rotação, retenção)

#### **Fontes de Dados**
- Lista prioritária de fontes (ordem de preferência)
- Lista de exclusão de fontes específicas
- Configurações de timeout e retry para cada fonte
- Headers HTTP personalizados se necessário

#### **Filtros de Eventos**
- **Detecção dinâmica de categorias**: Sistema que identifica automaticamente todas as categorias disponíveis nas fontes
- **Lista de inclusão configurável**: Permite especificar categorias específicas ou usar "*" para todas
- **Lista de exclusão de categorias**: Permite excluir categorias específicas
- **Filtros por país/região**: Configurável por localização
- **Filtros por tipo de evento**: Corrida, treino, classificação, etc.
- **Mapeamento inteligente**: Sistema que reconhece variações de nomes de categorias

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
- [ ] Script executa sem erros em macOS
- [ ] Coleta eventos do final de semana atual
- [ ] Gera arquivo .ics válido
- [ ] Arquivo importa corretamente no Google Calendar
- [ ] Eventos aparecem com informações corretas
- [ ] Logs informativos durante execução
- [ ] **Script identifica corretamente o fim de semana alvo**
- [ ] **Duplicatas são removidas mantendo dados da fonte prioritária**
- [ ] **Normalização de dados funciona corretamente**
- [ ] **Interface visual colorida e agradável durante execução**
- [ ] **Payloads raw de todas as integrações são salvos**
- [ ] **Log centralizado debug é gerado a cada execução**

---

**VALIDAÇÃO NECESSÁRIA:**
Estes requerimentos estão alinhados com suas expectativas? Há algo que gostaria de adicionar, modificar ou remover antes de prosseguirmos para o próximo passo?
