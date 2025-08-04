# Sistema de Logs e Configuração

Este documento descreve o sistema de logs e configuração do Motorsport Calendar, incluindo como configurar níveis de log, rotação de arquivos e retenção.

## Visão Geral

O sistema de logs do Motorsport Calendar foi projetado para fornecer informações detalhadas sobre a execução do aplicativo, facilitando a depuração e o monitoramento. Ele inclui:

- Registro em múltiplos níveis (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Rotação automática de logs
- Limpeza de logs antigos baseada em políticas de retenção
- Armazenamento de payloads para depuração

## Configuração de Logs

As configurações de log são definidas no arquivo `config/config.json` na seção `logging`. Consulte o [Guia de Configuração](../CONFIGURATION_GUIDE.md) para uma referência detalhada de todas as opções disponíveis:

```json
"logging": {
  "directory": "logs",
  "retention": {
    "enabled": true,
    "max_logs_to_keep": 10,
    "delete_older_than_days": 30
  },
  "levels": {
    "console": "INFO",
    "file": "DEBUG"
  }
}
```

### Opções de Configuração

- **directory**: Diretório onde os logs serão armazenados (padrão: `logs`)
- **retention**: Configurações de retenção de logs
  - **enabled**: Habilita/desabilita a limpeza automática de logs
  - **max_logs_to_keep**: Número máximo de arquivos de log a manter
  - **delete_older_than_days**: Exclui logs mais antigos que este número de dias
- **levels**: Níveis de log para diferentes saídas
  - **console**: Nível de log para saída no console
  - **file**: Nível de log para arquivos de log

## Estrutura de Diretórios

O sistema de logs cria a seguinte estrutura de diretórios:

```
logs/
├── motorsport_calendar.log     # Log principal
├── debug/                      # Logs de depuração detalhados
├── payloads/                   # Payloads armazenados para depuração
└── rotated_logs/               # Logs rotacionados
```

## Rotação de Logs

O sistema realiza rotação de logs automaticamente:

1. A cada execução, o log principal é movido para `rotated_logs/` com um carimbo de data/hora
2. Apenas os logs mais recentes são mantidos, conforme configurado
3. Logs antigos são removidos automaticamente com base nas políticas de retenção

## Boas Práticas

1. **Níveis de Log**
   - Use `DEBUG` para informações detalhadas de depuração
   - Use `INFO` para eventos normais de operação
   - Use `WARNING` para situações que podem exigir atenção
   - Use `ERROR` para erros que não impedem a execução
   - Use `CRITICAL` para erros fatais

2. **Armazenamento de Payloads**
   - Payloads grandes devem ser armazenados apenas quando necessário
   - Use `save_payload()` para armazenar dados de depuração

3. **Monitoramento**
   - Monitore regularmente o uso de espaço em disco
   - Ajuste as políticas de retenção conforme necessário

## Solução de Problemas

### Logs não estão sendo rotacionados
- Verifique se a permissão de escrita no diretório de logs
- Confirme se a configuração `retention.enabled` está como `true`
- Verifique se há erros no log principal

### Erro "ConfigManager object is not subscriptable"
- Certifique-se de usar `_get_log_config()` para acessar configurações
- Não acesse o ConfigManager diretamente como um dicionário

### Logs muito grandes
- Ajuste o nível de log para `INFO` ou superior em produção
- Revise as configurações de retenção para excluir logs antigos mais rapidamente

## Personalização

Para personalizar o comportamento de log, você pode:

1. Modificar o arquivo `config.json`
2. Estender a classe `Logger` para comportamentos personalizados
3. Implementar seus próprios manipuladores de log do Python

Para mais informações, consulte a documentação do Python sobre o módulo `logging`.
