# Notas de Versão

Este arquivo contém um registro acumulativo de todas as versões lançadas do projeto, com notas detalhadas sobre as mudanças em cada versão.

## Versão 0.5.1 (2025-08-09)
Rollback técnico da branch main para o snapshot exato do commit `9362503`.

### 🔄 Contexto
- PR #34: rollback seguro aplicando restauração completa da árvore para `9362503` em um único commit (histórico preservado).
- Tag de backup criada anteriormente: `backup/pre-rollback-9362503-20250808-222821`.

### 📌 O que mudou
- Revertidas mudanças introduzidas após `9362503` (algumas funcionalidades avançadas de logging, períodos de silêncio, workflow de issues e arquivamento iCal podem não estar disponíveis temporariamente).
- Reaplicado `.gitignore` para evitar versionamento de artefatos de teste e diretórios locais.
- CI/regression-tests não reintroduzido neste release (será revisitado futuramente).

### ✅ Impactos práticos
- O código volta a um estado estável anterior; documentação contém notas de pós-rollback para sinalizar possíveis divergências temporárias.
- Nenhuma migração de dados é necessária.

## Versão 0.5.0 (2025-08-04)
**Melhorias no Sistema de Logging e Configuração**

### 🚀 Novas Funcionalidades

- **Sistema de Logging Aprimorado**
  - Implementados códigos de erro estruturados para melhor rastreamento
  - Adicionado suporte a mensagens de erro com sugestões de correção
  - Melhorada a rotação e limpeza automática de logs
  - Níveis de log configuráveis por saída (console/arquivo)

- **Gerenciamento de Payloads**
  - Rotação automática baseada em quantidade e idade
  - Organização por fonte de dados
  - Configuração flexível de retenção
  - Limpeza inteligente de arquivos antigos

- **Validação de Configuração**
  - Módulo `config_validator.py` para validação centralizada
  - Validação de tipos e valores
  - Mensagens de erro detalhadas
  - Valores padrão sensatos

- **Períodos de Silêncio**
  - Validação robusta de configurações
  - Suporte a múltiplos períodos
  - Configuração flexível de dias e horários

- **Documentação**
  - Exemplos detalhados de configuração
  - Guia de códigos de erro
  - Referência completa das opções
  - Melhores práticas

## Versão 0.4.1 (2025-08-04)
**Correções de Bugs**

### 🐛 Correções de Bugs

- **Correção na Filtragem de Períodos de Silêncio**
  - Corrigido problema que causava a remoção de todos os eventos durante a filtragem
  - Melhorada a lógica de verificação de períodos ativos
  - Adicionada validação para eventos sem data
  - Melhorada a documentação dos métodos de filtragem

- **Correção no UIManager**
  - Atualizada chamada incorreta de `show_warning` para `show_warning_message`
  - Adicionada verificação de existência do método
  - Melhorada a mensagem de aviso exibida ao usuário

## Versão 0.4.0 (2025-08-03)
**Períodos de Silêncio**

### 🔇 Períodos de Silêncio

**Nova Funcionalidade Principal**: Implementação de períodos de silêncio configuráveis para filtrar eventos por horário.

#### Funcionalidades Adicionadas
- **Classe SilentPeriod**: Gerenciamento individual de períodos de silêncio
- **Classe SilentPeriodManager**: Gerenciamento de múltiplos períodos e filtragem de eventos
- **Configuração Flexível**: Períodos configuráveis via arquivo JSON
- **Suporte a Meia-Noite**: Períodos que cruzam a meia-noite (ex: 22:00-06:00)
- **Logs Detalhados**: Registro completo de eventos filtrados
- **Estatísticas**: Contadores de eventos filtrados nas estatísticas de processamento

#### Configuração
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
      }
    ]
  }
}
```

#### Comportamento
- Eventos durante períodos de silêncio são filtrados do arquivo iCal
- Eventos filtrados são registrados nos logs para auditoria
- Resumo de eventos filtrados exibido no terminal
- Não afeta a coleta ou processamento inicial dos eventos

#### Melhorias Técnicas
- Testes unitários completos (15 casos de teste)
- Validação robusta de configuração
- Tratamento de erros e casos extremos
- Integração transparente com o pipeline de processamento existente

#### Issue Relacionada
- **Issue #22**: ✨ Adicionar suporte a período de silêncio para eventos

## Versão 0.3.0 (2025-08-03)
**Correção de Links de Transmissão e Arquivos iCal**

### 🐛 Correções
- **Links de Transmissão**
  - Corrigida a perda de links de transmissão durante o processamento de eventos
  - Implementado tratamento adequado para diferentes formatos de links de streaming
  - Adicionada validação de URLs de streaming
  - Melhorada a formatação de links no arquivo iCal final

- **Arquivos iCal**
  - Implementada rotação automática de arquivos iCal antigos
  - Arquivos antigos são movidos para a subpasta `output/history/`
  - Mantido apenas o arquivo mais recente na pasta raiz de saída
  - Adicionada documentação sobre o sistema de arquivamento

### 🔧 Melhorias Técnicas
- Aprimorado o método `_normalize_streaming_links` para suportar múltiplos formatos de entrada
- Adicionada verificação de duplicação de links de streaming
- Melhor tratamento de erros durante o processamento de links
- Otimização no armazenamento de metadados dos eventos

## Versão 0.2.0 (2025-08-02)
**Workflow Unificado de Gestão de Issues**

### ✨ Novas Funcionalidades
- **Sistema de Importação de Issues**
  - Script `import_issues.py` para criação automática de issues no GitHub
  - Suporte a formatação Markdown completa nos corpos das issues
  - Importação em lote de múltiplas issues
  - Rastreamento de issues importadas

- **Estrutura de Diretórios Padronizada**
  - `open/`: Issues a serem processadas
  - `imported/`: Issues já importadas (com timestamp)
  - `closed/`: Issues resolvidas e fechadas
  - `templates/`: Modelos para novas issues

- **Templates de Issues**
  - Modelo para relatórios de bugs
  - Modelo para solicitações de funcionalidades
  - Documentação detalhada para cada tipo de issue

### 📚 Documentação
- Atualizado `README.md` com instruções detalhadas
- Adicionada seção de boas práticas
- Documentado fluxo completo de trabalho
- Incluídos exemplos de uso

### 🔧 Melhorias Técnicas
- Validação de dados nas issues
- Tratamento de erros aprimorado
- Suporte a metadados avançados
- Rastreamento de issues relacionadas

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

## Release (2025-08-09)
- Tipo: Fix
- Descrição: Corrige comparações naive/aware ao filtrar eventos por fim de semana.
- Impacto: Geração de iCal sem erros; 75 eventos processados.
- Arquivo: `output/motorsport_events_20250808.ics`
- Notas: Garantir timezone na configuração do projeto.
