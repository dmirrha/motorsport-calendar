# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Não Lançado]
### Corrigido
- **Issue #23**: Corrigido bug na filtragem de períodos de silêncio
  - Corrigida lógica de filtragem que estava removendo todos os eventos
  - Melhorada a verificação de períodos de silêncio ativos
  - Adicionada validação adicional para garantir que eventos sem data não sejam filtrados incorretamente
  - Atualizada a documentação dos métodos relacionados
- Corrigida chamada incorreta para `show_warning` no UIManager
  - Atualizado para usar o método correto `show_warning_message`
  - Adicionada verificação de existência do método para evitar erros
  - Melhorada a mensagem de aviso exibida ao usuário

### Adicionado
- **Gerenciamento de Arquivos iCal**
  - Implementado sistema de arquivamento automático de arquivos iCal antigos
  - Arquivos antigos são movidos para a subpasta `output/history/`
  - Mantido apenas o arquivo mais recente na pasta raiz de saída
  - Adicionada documentação sobre o sistema de arquivamento
- **Workflow de Issues**: Novo sistema unificado para gerenciamento de issues
  - Estrutura de diretórios padronizada (open/imported/closed/templates)
  - Script de importação automática com suporte a Markdown
  - Templates padronizados para issues
  - Documentação completa do fluxo de trabalho
  - Suporte a metadados e rastreamento de issues relacionadas
  - Processo automatizado para fechamento de issues
  - Integração com o CHANGELOG.md
- **Períodos de Silêncio**: Funcionalidade para filtrar eventos por horário configurável (Issue #22)
  - Classe `SilentPeriod` para gerenciar períodos individuais de silêncio
  - Classe `SilentPeriodManager` para gerenciar múltiplos períodos e filtragem de eventos
  - Configuração flexível de períodos de silêncio via arquivo JSON
  - Suporte a períodos que cruzam a meia-noite
  - Logs detalhados de eventos filtrados por período de silêncio

### Corrigido
- **Issue #20**: Corrigida perda de links de transmissão durante o processamento
  - Implementado tratamento adequado para diferentes formatos de links de streaming
  - Adicionada validação de URLs de streaming
  - Melhorada a formatação de links no arquivo iCal final
  - Adicionada verificação de duplicação de links de streaming
  - Melhor tratamento de erros durante o processamento de links
- Correção na preservação de links de transmissão durante o processamento de eventos (Issue #20)
- Melhoria na normalização de links de streaming para suportar diferentes formatos
- Validação e deduplicação de URLs de streaming
- **Issue #3**: Corrigida detecção de eventos sem data explícita na fonte Tomada de Tempo
  - Implementado suporte ao formato de data "SÁBADO – 02/08/2025"
  - Adicionada extração do contexto da programação do título/URL da página
  - Implementada associação de eventos sem data explícita ao contexto da programação
  - Melhorado suporte a formatos variados de horário (14h30, às 14:30, 14 horas e 30, etc.)
  - Adicionado campo `from_context` para rastreabilidade da origem da data
  - Criado script de teste automatizado para validação das correções
  - Todos os critérios de aceitação da issue atendidos com 100% dos testes passando

### Corrigido
- **Ambiente Python**: Atualizado para Python 3.11.5
  - Resolvido aviso de compatibilidade entre urllib3 v2+ e OpenSSL
  - Configurado ambiente via pyenv para gerenciamento de versões
  - Atualizadas dependências para versões compatíveis
  - Removido arquivo de debug não mais necessário (`debug_weekend_filter.py`)
  - Atualizado `.gitignore` para excluir arquivos de log e dados temporários

### Corrigido
- **Issue #5**: Corrigida detecção do final de semana atual na TomadaTempoSource
  - Corrigido parsing de datas brasileiras (DD/MM/YYYY vs MM/DD/YYYY)
  - Corrigida lógica de timezone para America/Sao_Paulo
  - Implementado filtro por range de datas para incluir apenas eventos do fim de semana vigente
  - Excluídos eventos de finais de semana futuros conforme especificado
  - Adicionados testes automatizados para validação da filtragem

- **Sistema de Logs**: Corrigido acesso seguro às configurações
  - Resolvido erro `'ConfigManager' object is not subscriptable` na limpeza de logs
  - Implementado método `_get_log_config` para acesso consistente às configurações
  - Melhorado tratamento de erros na rotação e limpeza de logs
  - Adicionada verificação de existência de diretórios antes de operações de arquivo

### Melhorado
- **Estrutura do Projeto**: Reorganização dos diretórios para melhor organização
  - Movidos arquivos de configuração para pasta `config/`
  - Atualizados imports para usar caminhos absolutos
  - Melhorada a organização do código fonte
  - Atualizada documentação para refletir a nova estrutura

### Adicionado
- Sistema de versionamento semântico
- Documentação do processo de releases
- Automação de geração de changelog
- Script de debug para análise de filtragem de fim de semana

## [0.1.0] - 2025-08-02
### Adicionado
- Sistema inicial de coleta de eventos de automobilismo
- Suporte a múltiplas fontes de dados
- Geração de arquivos iCal
- Interface de linha de comando
- Sistema de logging avançado
- Rotação automática de logs
- Sistema de importação de issues via JSON

### Melhorado
- Detecção de categorias de automobilismo
- Processamento de datas e fusos horários
- Tratamento de erros e recuperação

### Corrigido
- Problemas na detecção de eventos sem data
- Filtragem incorreta de eventos de fim de semana
- Problemas de codificação de caracteres

---
Nota: Este arquivo é gerado automaticamente. Para adicionar uma nova entrada, use o formato convencional de commit.
