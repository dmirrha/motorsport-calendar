# Notas de Versão

Este arquivo contém um registro acumulativo de todas as versões lançadas do projeto, com notas detalhadas sobre as mudanças em cada versão.

## Versão 0.1.3 (2025-08-02)
**Melhorias no Sistema de Logs e Configuração**

### 🐛 Correções
- **Sistema de Logs**: Corrigido acesso seguro às configurações
  - Resolvido erro `'ConfigManager' object is not subscriptable` na limpeza de logs
  - Implementado método `_get_log_config` para acesso consistente às configurações
  - Melhorado tratamento de erros na rotação e limpeza de logs
  - Adicionada verificação de existência de diretórios antes de operações de arquivo

### 📚 Documentação
- Adicionado arquivo `LOGGING_AND_CONFIGURATION.md` com documentação detalhada sobre:
  - Configuração de níveis de log
  - Estrutura de diretórios de logs
  - Políticas de retenção e rotação
  - Solução de problemas comuns
  - Boas práticas para uso do sistema de logs

## Versão 0.1.2 (2025-08-02)
**Melhorias na Estrutura do Projeto**

### 🚀 Melhorias
- **Reorganização da Estrutura de Diretórios**:
  - Movidos arquivos de configuração para diretório `config/`
  - Atualizados imports para usar caminhos absolutos
  - Melhorada a organização do código fonte
  - Documentação atualizada para refletir a nova estrutura

## Versão 0.1.1 (2025-08-02)
**Correção Crítica de Filtragem de Fim de Semana**

### 🐛 Correções
- **Issue #5**: Corrigida detecção do final de semana atual na TomadaTempoSource
  - **Problema Resolvido**: Sistema estava incluindo eventos de finais de semana futuros
  - **Correção de Parsing**: Datas brasileiras (DD/MM/YYYY) agora interpretadas corretamente
  - **Correção de Timezone**: Implementado suporte consistente ao timezone America/Sao_Paulo
  - **Filtro Aprimorado**: Implementado filtro por range de datas para limitar coleta ao fim de semana vigente
  - **Testes Adicionados**: Criados testes automatizados para validação da filtragem

### 📋 Detalhes Técnicos
- Método `parse_date_time` na BaseSource atualizado para priorizar formato brasileiro
- Método `collect_events` na TomadaTempoSource corrigido para calcular range correto do fim de semana
- Método `_get_next_weekend` ajustado para retornar sexta-feira do fim de semana atual
- Script de debug criado para análise detalhada da filtragem

### ✅ Critérios de Aceitação Atendidos
- 100% dos eventos exibidos pertencem ao final de semana atual
- Nenhum evento futuro incluído indevidamente
- Transição de semanas funciona corretamente
- Desempenho mantido
- Timezone America/Sao_Paulo respeitado

## Versão 0.1.0 (2025-08-02)
**Versão Inicial**

### 🚀 Novas Funcionalidades
- **Sistema de Coleta de Eventos**
  - Coleta automática de eventos de múltiplas fontes
  - Suporte a diferentes categorias de automobilismo
  - Geração de arquivos iCal para importação no Google Calendar

- **Interface de Linha de Comando**
  - Interface intuitiva com feedback visual
  - Opções de configuração flexíveis
  - Logs detalhados para depuração

- **Sistema de Logging**
  - Rotação automática de arquivos de log
  - Níveis de log configuráveis
  - Retenção personalizável de logs

- **Gerenciamento de Issues**
  - Importação automatizada de issues via JSON
  - Rastreamento de bugs e melhorias
  - Documentação detalhada do processo

### 🛠 Melhorias
- Aprimoramento na detecção de categorias
- Melhor processamento de datas e fusos horários
- Tratamento de erros mais robusto

### 🐛 Correções
- Corrigida detecção de eventos sem data explícita
- Ajustada filtragem de eventos de fim de semana
- Corrigidos problemas de codificação de caracteres

### 📦 Dependências
- Python 3.8+
- Bibliotecas listadas em `requirements.txt`

### 📝 Notas de Atualização
Esta é a versão inicial do projeto, contendo toda a funcionalidade básica para coleta e exportação de eventos de automobilismo.
