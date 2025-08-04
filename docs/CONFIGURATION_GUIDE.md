# Guia de Configuração do Motorsport Calendar Generator

Este documento descreve todas as opções de configuração disponíveis no arquivo `config.json` do Motorsport Calendar Generator.

## Visão Geral

O arquivo de configuração é dividido em várias seções principais, cada uma responsável por aspectos específicos do comportamento da aplicação. Todas as configurações são opcionais, com valores padrão sensíveis fornecidos internamente.

## Seção: `general`

Configurações gerais da aplicação.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `timezone` | string | `"America/Sao_Paulo"` | Fuso horário padrão para os eventos |
| `language` | string | `"pt-BR"` | Idioma preferido para os textos da aplicação |
| `log_level` | string | `"INFO"` | Nível de log global (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `output_directory` | string | `"./output"` | Diretório para salvar os arquivos iCal gerados |

### Subseção: `visual_interface`

Configurações da interface visual.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita/desabilita a interface visual |
| `colors` | boolean | `true` | Habilita/desabilita cores na saída do console |
| `progress_bars` | boolean | `true` | Habilita/desabilita barras de progresso |
| `icons` | boolean | `true` | Habilita/desabilita ícones na saída |

### Subseção: `advanced_logging`

Configurações avançadas de log.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `debug_logs` | boolean | `true` | Habilita logs de depuração detalhados |
| `payload_storage` | boolean | `true` | Habilita armazenamento de payloads brutos |
| `log_rotation` | boolean | `true` | Habilita rotação automática de logs |
| `retention_days` | number | `30` | Número de dias para reter logs antigos |

### Subseção: `silent_periods`

Define períodos de silêncio onde notificações são suprimidas.

Cada período contém:

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `enabled` | boolean | Não | Se o período está ativo |
| `name` | string | Sim | Nome descritivo do período |
| `start_time` | string | Sim | Hora de início (formato HH:MM) |
| `end_time` | string | Sim | Hora de término (formato HH:MM) |
| `days_of_week` | array | Sim | Dias da semana (ex: ["monday", "tuesday"]) |

## Seção: `data_sources`

Configurações das fontes de dados.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `priority_order` | array | `["tomada_tempo"]` | Ordem de prioridade das fontes |
| `excluded_sources` | array | `[]` | Fontes a serem ignoradas |
| `timeout_seconds` | number | `10` | Timeout em segundos para requisições |
| `retry_attempts` | number | `3` | Número de tentativas em caso de falha |
| `rate_limit_delay` | number | `1.0` | Atraso entre requisições (segundos) |
| `user_agents` | array | Lista padrão | User-Agents para requisições HTTP |

## Seção: `event_filters`

Filtros para processamento de eventos.

### Subseção: `category_detection`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita detecção automática de categorias |
| `learning_mode` | boolean | `true` | Habilita aprendizado de novas categorias |
| `confidence_threshold` | number | `0.7` | Limite de confiança para detecção (0-1) |

### Outros filtros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `included_categories` | array | `["*"]` | Categorias a incluir ("*" para todas) |
| `excluded_categories` | array | `[]` | Categorias a excluir |
| `included_countries` | array | `[]` | Países a incluir |
| `excluded_countries` | array | `[]` | Países a excluir |

### Subseção: `event_types`

Habilita/desabilita tipos específicos de eventos.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `race` | boolean | `true` | Corridas principais |
| `qualifying` | boolean | `true` | Treinos classificatórios |
| `practice` | boolean | `false` | Treinos livres |
| `sprint` | boolean | `true` | Corridas de sprint |
| `other` | boolean | `false` | Outros tipos de eventos |

### Subseção: `weekend_detection`

Configura a detecção de finais de semana.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `algorithm` | string | `"first_event_based"` | Algoritmo de detecção |
| `days_range` | array | `["friday", "saturday", "sunday"]` | Dias considerados do final de semana |
| `extend_to_thursday` | boolean | `false` | Estende para quinta-feira |
| `extend_to_monday` | boolean | `false` | Estende para segunda-feira |

## Seção: `ical_parameters`

Configurações para geração de arquivos iCal.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `calendar_name` | string | `"Motorsport Events"` | Nome do calendário |
| `calendar_description` | string | `"Weekend motorsport events automatically collected"` | Descrição do calendário |
| `timezone` | string | `"America/Sao_Paulo"` | Fuso horário do calendário |
| `default_duration_minutes` | number | `120` | Duração padrão dos eventos (minutos) |
| `event_category` | string | `"SPORTS"` | Categoria dos eventos |
| `event_priority` | string | `"NORMAL"` | Prioridade dos eventos |
| `event_status` | string | `"CONFIRMED"` | Status dos eventos |
| `include_streaming_links` | boolean | `true` | Inclui links de transmissão |
| `include_location` | boolean | `true` | Inclui localização |
| `include_description` | boolean | `true` | Inclui descrição detalhada |

### Subseção: `reminders`

Lembretes para os eventos.

Cada lembrete contém:

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `minutes` | number | Sim | Minutos antes do evento |
| `method` | string | Sim | Método ("popup" ou "email") |

## Seção: `streaming_providers`

Configura provedores de streaming por região.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `region` | string | `"BR"` | Região padrão |
| `mappings` | object | - | Mapeamento de categorias para provedores |
| `fallback_providers` | object | - | Provedores alternativos por região |

## Seção: `deduplication`

Configurações para remoção de eventos duplicados.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `algorithm` | string | `"fuzzy_matching"` | Algoritmo de deduplicação |
| `name_similarity_threshold` | number | `0.85` | Limite de similaridade de nomes (0-1) |
| `time_tolerance_minutes` | number | `30` | Tolerância de tempo (minutos) |
| `location_matching` | boolean | `true` | Considerar localização na deduplicação |
| `category_matching` | boolean | `true` | Considerar categoria na deduplicação |
| `source_priority_resolution` | boolean | `true` | Resolver conflitos por prioridade da fonte |

## Seção: `category_mapping`

Mapeamento de categorias e classificação.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `learning_enabled` | boolean | `true` | Habilita aprendizado de mapeamentos |
| `custom_mappings` | object | - | Mapeamentos personalizados de nomes para categorias |
| `type_classification` | object | - | Classificação de tipos de veículos |

## Seção: `logging`

Configurações detalhadas de log.

### Subseção: `file_structure`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `main_log` | string | `"logs/motorsport_calendar.log"` | Arquivo de log principal |
| `debug_directory` | string | `"logs/debug"` | Diretório para logs de depuração |
| `payload_directory` | string | `"logs/payloads"` | Diretório para armazenar payloads |

### Subseção: `retention`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita retenção de logs |
| `max_logs_to_keep` | number | `10` | Número máximo de arquivos de log |
| `max_payloads_to_keep` | number | `20` | Número máximo de payloads |
| `delete_older_than_days` | number | `30` | Excluir arquivos mais antigos que X dias |

### Subseção: `levels`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `console` | string | `"INFO"` | Nível de log para console |
| `file` | string | `"DEBUG"` | Nível de log para arquivo |
| `debug_file` | string | `"DEBUG"` | Nível de log para arquivo de depuração |

### Subseção: `format`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `console` | string | Formato padrão | Formato para saída no console |
| `file` | string | Formato detalhado | Formato para arquivos de log |

### Subseção: `rotation`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita rotação de logs |
| `max_size_mb` | number | `10` | Tamanho máximo do arquivo (MB) |
| `backup_count` | number | `5` | Número de backups a manter |

### Subseção: `payload_settings`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `save_raw` | boolean | `true` | Salva payloads brutos |
| `pretty_print` | boolean | `true` | Formatação legível dos payloads |
| `include_headers` | boolean | `true` | Inclui cabeçalhos HTTP |
| `separate_by_source` | boolean | `true` | Separa por fonte de dados |

## Exemplo Completo

Consulte `config/config.example.json` para um exemplo completo de configuração com todas as opções.

## Atualizando a Configuração

1. Faça uma cópia de segurança do seu arquivo `config.json` atual
2. Atualize as seções necessárias
3. Teste a configuração com: `python motorsport_calendar.py --validate-config`
4. Verifique os logs para possíveis avisos ou erros

## Solução de Problemas

- **Configuração inválida**: Verifique a sintaxe JSON e os valores aceitos
- **Permissões**: Certifique-se de que a aplicação tem permissão para escrever nos diretórios especificados
- **Logs**: Consulte o arquivo de log principal para mensagens de erro detalhadas
