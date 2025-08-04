"""
Validação de configuração para o Logger e componentes relacionados.

Este módulo fornece funções para validar e padronizar as configurações
do logger e do sistema de gerenciamento de payloads.
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from .error_codes import ErrorCode

class ConfigValidationError(ValueError):
    """Exceção lançada quando uma configuração inválida é detectada."""
    def __init__(self, message: str, error_code: str, field: str = None):
        self.message = message
        self.error_code = error_code
        self.field = field
        super().__init__(f"[{error_code}] {message}")

def validate_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Valida e padroniza a configuração de logging."""
    if not config:
        raise ConfigValidationError(
            "Configuração de logging não fornecida",
            ErrorCode.CONFIG_MISSING_REQUIRED,
            "logging"
        )
    
    # Configurações padrão
    default_config = {
        'file_structure': {
            'main_log': 'logs/motorsport_calendar.log',
            'debug_directory': 'logs/debug',
            'payload_directory': 'logs/payloads'
        },
        'retention': {
            'enabled': True,
            'max_logs_to_keep': 10,
            'max_payloads_to_keep': 20,
            'delete_older_than_days': 30
        },
        'levels': {
            'console': 'INFO',
            'file': 'DEBUG',
            'debug_file': 'DEBUG'
        },
        'format': {
            'console': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        },
        'rotation': {
            'enabled': True,
            'max_size_mb': 10,
            'backup_count': 5
        },
        'payload_settings': {
            'save_raw': True,
            'pretty_print': True,
            'include_headers': True,
            'separate_by_source': True
        }
    }
    
    # Mescla com as configurações fornecidas
    merged = {**default_config, **config}
    
    # Validação dos níveis de log
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    for level_type in ['console', 'file', 'debug_file']:
        level = merged['levels'].get(level_type, 'INFO').upper()
        if level not in valid_levels:
            raise ConfigValidationError(
                f"Nível de log inválido para {level_type}: {level}",
                ErrorCode.CONFIG_VALIDATION_ERROR,
                f"levels.{level_type}"
            )
        merged['levels'][level_type] = level
    
    # Validação de valores numéricos
    try:
        # Retenção
        retention = merged['retention']
        retention['max_logs_to_keep'] = max(1, int(retention.get('max_logs_to_keep', 10)))
        retention['max_payloads_to_keep'] = max(1, int(retention.get('max_payloads_to_keep', 20)))
        retention['delete_older_than_days'] = max(1, int(retention.get('delete_older_than_days', 30)))
        
        # Rotação
        rotation = merged['rotation']
        rotation['max_size_mb'] = max(1, int(rotation.get('max_size_mb', 10)))
        rotation['backup_count'] = max(1, int(rotation.get('backup_count', 5)))
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor numérico inválido na configuração: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            "retention/rotation"
        ) from e
    
    # Validação de diretórios
    try:
        file_structure = merged['file_structure']
        
        # Valida e cria diretórios necessários
        for dir_type, dir_path in file_structure.items():
            try:
                # Converte para caminho absoluto se for relativo
                dir_path = Path(dir_path)
                if not dir_path.is_absolute():
                    dir_path = Path.cwd() / dir_path
                
                # Cria o diretório se não existir
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Verifica permissões de escrita
                if not os.access(dir_path, os.W_OK):
                    raise ConfigValidationError(
                        f"Sem permissão de escrita no diretório: {dir_path}",
                        ErrorCode.OUTPUT_PERMISSION_ERROR,
                        f"file_structure.{dir_type}"
                    )
                
                # Atualiza o caminho no dicionário de configuração
                file_structure[dir_type] = str(dir_path.absolute())
                
            except Exception as e:
                if dir_type == 'main_log':
                    # Para o arquivo de log principal, tenta usar um local alternativo
                    alt_path = Path.cwd() / 'logs' / f"{dir_type}.log"
                    try:
                        alt_path.parent.mkdir(parents=True, exist_ok=True)
                        alt_path.touch()
                        file_structure[dir_type] = str(alt_path.absolute())
                        logging.warning(
                            f"[CONFIG-WARNING] Usando caminho alternativo para {dir_type}: {alt_path}"
                        )
                    except Exception as alt_e:
                        raise ConfigValidationError(
                            f"Falha ao configurar diretório de log: {e}",
                            ErrorCode.OUTPUT_WRITE_ERROR,
                            f"file_structure.{dir_type}"
                        ) from alt_e
                else:
                    raise ConfigValidationError(
                        f"Erro ao validar diretório {dir_type}: {e}",
                        ErrorCode.OUTPUT_WRITE_ERROR,
                        f"file_structure.{dir_type}"
                    ) from e
        
        # Atualiza o dicionário com os caminhos validados
        merged['file_structure'] = file_structure
        
    except Exception as e:
        if not isinstance(e, ConfigValidationError):
            raise ConfigValidationError(
                f"Erro inesperado na validação de diretórios: {e}",
                ErrorCode.CONFIG_VALIDATION_ERROR,
                "file_structure"
            ) from e
        raise
    
    return merged


def validate_payload_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Valida e padroniza as configurações de payload."""
    if not settings:
        settings = {}
    
    default_settings = {
        'save_raw': True,
        'pretty_print': True,
        'include_headers': True,
        'separate_by_source': True,
        'compress': True,
        'max_files_per_source': 50,
        'max_age_days': 30
    }
    
    # Mescla com as configurações fornecidas
    merged = {**default_settings, **settings}
    
    # Converte valores booleanos
    for bool_key in ['save_raw', 'pretty_print', 'include_headers', 'separate_by_source', 'compress']:
        if bool_key in settings:
            merged[bool_key] = bool(settings[bool_key])
    
    # Valida valores numéricos
    try:
        merged['max_files_per_source'] = max(1, int(merged.get('max_files_per_source', 50)))
        merged['max_age_days'] = max(1, int(merged.get('max_age_days', 30)))
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor numérico inválido nas configurações de payload: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            "payload_settings"
        ) from e
    
    return merged


# Adicionando função validate_silent_periods ao final do arquivo

def validate_silent_periods(periods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Valida e padroniza os períodos de silêncio.
    
    Args:
        periods: Lista de dicionários com configurações de períodos de silêncio
        
    Returns:
        Lista com os períodos de silêncio validados e padronizados
    """
    if not isinstance(periods, list):
        return []
    
    valid_periods = []
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for i, period in enumerate(periods, 1):
        try:
            if not isinstance(period, dict):
                logging.warning(
                    f"[CONFIG-WARNING] Período de silêncio inválido (não é um dicionário): {period}"
                )
                continue
            
            # Valida campos obrigatórios
            if 'name' not in period or not period['name']:
                period['name'] = f"Período {i}"
            
            # Valida status (habilitado/desabilitado)
            period['enabled'] = bool(period.get('enabled', True))
            
            # Valida horário de início e fim
            for time_key in ['start_time', 'end_time']:
                if time_key not in period:
                    raise ConfigValidationError(
                        f"Campo obrigatório ausente: {time_key}",
                        ErrorCode.CONFIG_MISSING_REQUIRED,
                        f"silent_periods[{i}].{time_key}"
                    )
                
                # Tenta converter para o formato HH:MM
                try:
                    time_str = str(period[time_key])
                    if ':' not in time_str:
                        raise ValueError("Formato inválido, use HH:MM")
                    
                    hours, minutes = map(int, time_str.split(':'))
                    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                        raise ValueError("Horas devem estar entre 00-23 e minutos entre 00-59")
                    
                    # Padroniza o formato
                    period[time_key] = f"{hours:02d}:{minutes:02d}"
                    
                except (ValueError, AttributeError) as e:
                    raise ConfigValidationError(
                        f"Formato de hora inválido para {time_key}: {period[time_key]}",
                        ErrorCode.CONFIG_VALIDATION_ERROR,
                        f"silent_periods[{i}].{time_key}"
                    ) from e
            
            # Valida dias da semana
            days = period.get('days_of_week', [])
            if not isinstance(days, list):
                days = [days] if days else []
            
            # Converte para minúsculas e remove duplicatas
            days = list({str(day).strip().lower() for day in days})
            
            # Filtra dias inválidos
            valid_days = [day for day in days if day in weekdays]
            
            if not valid_days:
                logging.warning(
                    f"[CONFIG-WARNING] Nenhum dia da semana válido para o período "
                    f"{period['name']}. Usando todos os dias."
                )
                valid_days = weekdays.copy()
            
            period['days_of_week'] = valid_days
            valid_periods.append(period)
            
        except Exception as e:
            logging.error(
                f"[CONFIG-ERROR] Erro ao validar período de silêncio {i}: {e}",
                exc_info=True
            )
    
    return valid_periods
