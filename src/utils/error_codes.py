"""
Códigos de erro padronizados para o projeto Motorsport Calendar.

Este módulo define códigos de erro estruturados para facilitar o rastreamento
e tratamento consistente de erros em toda a aplicação.

Cada código de erro segue o formato:
- PREFIXO: Identificador do módulo (ex: 'CONFIG', 'LOGGER', 'SOURCE')
- CÓDIGO: Número único de 4 dígitos
- SEVERIDADE: Nível de severidade do erro (INFO, WARNING, ERROR, CRITICAL)

Exemplo de uso:
    raise ValueError(
        f"[{ErrorCode.CONFIG_INVALID_FORMAT}] "
        "Formato de arquivo de configuração inválido"
    )
"""
from enum import Enum

class ErrorCode(str, Enum):
    """Códigos de erro padronizados para a aplicação."""
    
    # Erros de Configuração (1000-1999)
    CONFIG_FILE_NOT_FOUND = "CONFIG-1000-ERROR"
    CONFIG_INVALID_JSON = "CONFIG-1001-ERROR"
    CONFIG_VALIDATION_ERROR = "CONFIG-1002-ERROR"
    CONFIG_MISSING_REQUIRED = "CONFIG-1003-ERROR"
    
    # Erros de Logging (2000-2999)
    LOGGER_INIT_FAILED = "LOGGER-2000-CRITICAL"
    LOG_FILE_WRITE_ERROR = "LOGGER-2001-ERROR"
    LOG_ROTATION_FAILED = "LOGGER-2002-ERROR"
    LOG_RETENTION_CLEANUP_FAILED = "LOGGER-2003-WARNING"
    
    # Erros de Fontes de Dados (3000-3999)
    SOURCE_CONNECTION_ERROR = "SOURCE-3000-ERROR"
    SOURCE_TIMEOUT = "SOURCE-3001-ERROR"
    SOURCE_RATE_LIMIT = "SOURCE-3002-WARNING"
    SOURCE_PARSE_ERROR = "SOURCE-3003-ERROR"
    SOURCE_AUTH_ERROR = "SOURCE-3004-ERROR"
    
    # Erros de Processamento (4000-4999)
    PROCESSOR_VALIDATION_ERROR = "PROCESS-4000-ERROR"
    PROCESSOR_NORMALIZATION_ERROR = "PROCESS-4001-ERROR"
    
    # Erros de Saída (5000-5999)
    OUTPUT_WRITE_ERROR = "OUTPUT-5000-ERROR"
    OUTPUT_PERMISSION_ERROR = "OUTPUT-5001-ERROR"
    OUTPUT_FORMAT_ERROR = "OUTPUT-5002-ERROR"
    
    # Erros de Sistema (9000-9999)
    SYSTEM_UNEXPECTED = "SYSTEM-9000-CRITICAL"
    SYSTEM_RESOURCE_LIMIT = "SYSTEM-9001-ERROR"
    SYSTEM_DEPENDENCY_ERROR = "SYSTEM-9002-ERROR"


def get_error_suggestions(error_code: ErrorCode) -> str:
    """Retorna sugestões de correção para códigos de erro conhecidos.
    
    Args:
        error_code: Código de erro para o qual se deseja obter sugestões.
        
    Returns:
        String com sugestões de correção ou mensagem genérica se o código não for reconhecido.
    """
    suggestions = {
        # Configuração
        ErrorCode.CONFIG_FILE_NOT_FOUND: (
            "Verifique se o arquivo de configuração existe no caminho especificado. "
            "Considere copiar o arquivo de exemplo (config.example.json) se for a primeira execução."
        ),
        ErrorCode.CONFIG_INVALID_JSON: (
            "Verifique se o arquivo de configuração contém um JSON válido. "
            "Use um validador JSON para identificar problemas de sintaxe."
        ),
        ErrorCode.CONFIG_VALIDATION_ERROR: (
            "Verifique se todos os campos obrigatórios estão presentes e com valores válidos. "
            "Consulte a documentação para o formato esperado."
        ),
        
        # Logging
        ErrorCode.LOGGER_INIT_FAILED: (
            "Verifique as permissões de escrita no diretório de logs. "
            "Certifique-se de que o processo tem permissão para criar/editar arquivos."
        ),
        ErrorCode.LOG_FILE_WRITE_ERROR: (
            "Não foi possível gravar no arquivo de log. Verifique as permissões de escrita "
            "e se o arquivo não está sendo usado por outro processo."
        ),
        
        # Fontes de Dados
        ErrorCode.SOURCE_CONNECTION_ERROR: (
            "Verifique sua conexão com a internet e se o servidor da fonte de dados está acessível. "
            "Se o problema persistir, a fonte pode estar temporariamente indisponível."
        ),
        ErrorCode.SOURCE_RATE_LIMIT: (
            "Muitas requisições em um curto período. Aguarde alguns instantes antes de tentar novamente. "
            "Considere aumentar o intervalo entre requisições na configuração."
        ),
        
        # Processamento
        ErrorCode.PROCESSOR_VALIDATION_ERROR: (
            "Um ou mais eventos não atenderam aos critérios de validação. "
            "Verifique os logs para detalhes sobre os campos inválidos."
        ),
        
        # Saída
        ErrorCode.OUTPUT_WRITE_ERROR: (
            "Não foi possível gravar o arquivo de saída. Verifique se o diretório de saída existe "
            "e se o processo tem permissões de escrita."
        ),
        ErrorCode.OUTPUT_PERMISSION_ERROR: (
            "Permissão negada ao tentar gravar o arquivo de saída. "
            "Verifique as permissões do diretório e do arquivo de destino."
        ),
        
        # Sistema
        ErrorCode.SYSTEM_UNEXPECTED: (
            "Ocorreu um erro inesperado. Consulte os logs para obter mais detalhes. "
            "Se o problema persistir, considere abrir uma issue no repositório do projeto."
        ),
        ErrorCode.SYSTEM_RESOURCE_LIMIT: (
            "O sistema está sem recursos disponíveis (memória, espaço em disco, etc.). "
            "Tente liberar recursos ou aumentar os limites do sistema."
        ),
    }
    
    return suggestions.get(error_code, 
        "Consulte a documentação para obter ajuda com este código de erro."
    )


def get_error_severity(error_code: ErrorCode) -> str:
    """Retorna a severidade de um código de erro.
    
    Args:
        error_code: Código de erro.
        
    Returns:
        String indicando a severidade (INFO, WARNING, ERROR, CRITICAL).
    """
    if not error_code:
        return "UNKNOWN"
    
    # Extrai a severidade do código (última parte após o hífen)
    parts = error_code.split('-')
    if len(parts) >= 3:
        return parts[2]
    return "UNKNOWN"
