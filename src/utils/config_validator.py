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


def validate_data_sources_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Valida e padroniza a configuração da seção data_sources.
    
    Campos validados (com defaults):
    - priority_order: list[str]
    - excluded_sources: list[str]
    - timeout_seconds: int > 0 (default 10)
    - max_concurrent_sources: int >= 1 (default 3)
    - collection_timeout_seconds: int > 0 (default 300)
    - use_process_pool: bool (default False)
    - per_source_timeout_seconds: float > 0 (opcional; se ausente ou inválido, não aplicado)
    - retry_attempts: int >= 0 (legado)
    - retry_failed_sources: bool (default True)
    - max_retries: int >= 0 (default 1; fallback em retry_attempts se ausente)
    - retry_backoff_seconds: float >= 0 (default 0.5)
    - rate_limit_delay: float >= 0 (default 1.0)
    - user_agents: list[str]
    
    Returns:
        Dicionário normalizado com os valores validados.
    """
    if config is None:
        config = {}

    if not isinstance(config, dict):
        raise ConfigValidationError(
            "Configuração de data_sources deve ser um objeto",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            "data_sources"
        )

    merged: Dict[str, Any] = {**config}

    # Listas de strings
    def _normalize_str_list(value: Any, field: str) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            out: List[str] = []
            for v in value:
                if v is None:
                    continue
                s = str(v).strip()
                if s:
                    out.append(s)
            # remove duplicatas mantendo ordem
            seen = set()
            uniq: List[str] = []
            for s in out:
                if s not in seen:
                    seen.add(s)
                    uniq.append(s)
            return uniq
        # se não for lista, tenta converter único valor
        s = str(value).strip()
        return [s] if s else []

    merged['priority_order'] = _normalize_str_list(merged.get('priority_order', ["tomada_tempo"]), 'priority_order')
    merged['excluded_sources'] = _normalize_str_list(merged.get('excluded_sources', []), 'excluded_sources')
    merged['user_agents'] = _normalize_str_list(merged.get('user_agents', []), 'user_agents')

    # timeout_seconds: int > 0
    try:
        timeout = int(merged.get('timeout_seconds', 10))
        if timeout <= 0:
            raise ValueError("timeout_seconds deve ser > 0")
        merged['timeout_seconds'] = timeout
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para timeout_seconds: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'data_sources.timeout_seconds'
        ) from e

    # max_concurrent_sources: int >= 1
    try:
        mcs = int(merged.get('max_concurrent_sources', 3))
        if mcs < 1:
            raise ValueError("max_concurrent_sources deve ser >= 1")
        merged['max_concurrent_sources'] = mcs
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para max_concurrent_sources: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'data_sources.max_concurrent_sources'
        ) from e

    # collection_timeout_seconds: int > 0
    try:
        cts = int(merged.get('collection_timeout_seconds', 300))
        if cts <= 0:
            raise ValueError("collection_timeout_seconds deve ser > 0")
        merged['collection_timeout_seconds'] = cts
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para collection_timeout_seconds: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'data_sources.collection_timeout_seconds'
        ) from e

    # use_process_pool: bool
    upp = merged.get('use_process_pool', False)
    merged['use_process_pool'] = bool(upp)

    # per_source_timeout_seconds: float > 0 (opcional)
    try:
        if 'per_source_timeout_seconds' in merged and merged.get('per_source_timeout_seconds') is not None:
            pst = float(merged.get('per_source_timeout_seconds'))
            if pst <= 0:
                # se não for válido, remove para sinalizar que não deve ser aplicado
                merged['per_source_timeout_seconds'] = None
            else:
                merged['per_source_timeout_seconds'] = pst
        else:
            # não define quando ausente
            merged.pop('per_source_timeout_seconds', None)
    except (ValueError, TypeError) as e:
        # em caso de erro, remove para não aplicar
        merged.pop('per_source_timeout_seconds', None)

    # rate_limit_delay: float >= 0
    try:
        rld = float(merged.get('rate_limit_delay', 1.0))
        if rld < 0:
            raise ValueError("rate_limit_delay deve ser >= 0")
        merged['rate_limit_delay'] = rld
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para rate_limit_delay: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'data_sources.rate_limit_delay'
        ) from e

    # retry_failed_sources: bool
    rfs = merged.get('retry_failed_sources', True)
    merged['retry_failed_sources'] = bool(rfs)

    # retry_attempts (legado) e max_retries
    # tenta normalizar ambos e aplicar precedence a max_retries quando presente
    retry_attempts_val: Optional[int] = None
    if 'retry_attempts' in merged:
        try:
            retry_attempts_val = max(0, int(merged.get('retry_attempts', 3)))
            merged['retry_attempts'] = retry_attempts_val
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(
                f"Valor inválido para retry_attempts: {e}",
                ErrorCode.CONFIG_VALIDATION_ERROR,
                'data_sources.retry_attempts'
            ) from e

    try:
        if 'max_retries' in merged:
            mr = max(0, int(merged.get('max_retries', 1)))
        else:
            # fallback no legado
            mr = max(0, int(merged.get('retry_attempts', 1)))
        merged['max_retries'] = mr
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para max_retries: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'data_sources.max_retries'
        ) from e

    # retry_backoff_seconds: float >= 0
    try:
        rbs = float(merged.get('retry_backoff_seconds', 0.5))
        if rbs < 0:
            raise ValueError("retry_backoff_seconds deve ser >= 0")
        merged['retry_backoff_seconds'] = rbs
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para retry_backoff_seconds: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'data_sources.retry_backoff_seconds'
        ) from e

    return merged

def validate_ai_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Valida e padroniza a configuração da seção ai.
    
    Estrutura validada (com defaults):
    - enabled: bool (default False)
    - device: str in {auto,cpu,cuda,mps} (default 'auto')
    - batch_size: int >= 1 (default 16)
    - thresholds:
        - category: float entre 0 e 1 (default 0.75)
        - dedup: float entre 0 e 1 (default 0.85)
    - onnx:
        - enabled: bool (default False)
        - providers: list[str] in {cpu,cuda,coreml,mps} (default ['cpu'])
        - provider: str legado (mantido para compatibilidade; convertido em lista)
        - opset: int >= 11 (default 17)
        - model_path: str opcional (caminho para modelo ONNX local)
        - intra_op_num_threads: int opcional >= 1
        - inter_op_num_threads: int opcional >= 1
    - cache:
        - enabled: bool (default True)
        - dir: caminho gravável (default 'cache/embeddings')
        - ttl_days: int >= 0 (default 30)
    """
    if config is None:
        config = {}
    if not isinstance(config, dict):
        raise ConfigValidationError(
            "Configuração de ai deve ser um objeto",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            "ai"
        )

    merged: Dict[str, Any] = {**config}

    # enabled
    merged['enabled'] = bool(merged.get('enabled', False))

    # device
    device = str(merged.get('device', 'auto')).strip().lower()
    allowed_devices = {'auto', 'cpu', 'cuda', 'mps'}
    if device not in allowed_devices:
        raise ConfigValidationError(
            f"Valor inválido para ai.device: {device}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.device'
        )
    merged['device'] = device

    # batch_size
    try:
        bs = int(merged.get('batch_size', 16))
        if bs < 1:
            raise ValueError("batch_size deve ser >= 1")
        merged['batch_size'] = bs
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para ai.batch_size: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.batch_size'
        ) from e

    # thresholds
    thresholds = merged.get('thresholds', {}) or {}
    try:
        cat = float(thresholds.get('category', 0.75))
        ded = float(thresholds.get('dedup', 0.85))
        if not (0.0 <= cat <= 1.0):
            raise ValueError('category deve estar entre 0 e 1')
        if not (0.0 <= ded <= 1.0):
            raise ValueError('dedup deve estar entre 0 e 1')
        merged['thresholds'] = {'category': cat, 'dedup': ded}
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido em ai.thresholds: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.thresholds'
        ) from e

    # onnx
    onnx = merged.get('onnx', {}) or {}
    onnx_enabled = bool(onnx.get('enabled', False))
    # Providers: aceitar lista nova ou string legado
    allowed_providers = { 'cpu', 'cuda', 'coreml', 'mps' }
    providers_val = onnx.get('providers')
    if providers_val is None:
        # compatibilidade: 'provider' (string)
        prov_legacy = str(onnx.get('provider', 'cpu')).strip().lower()
        providers: List[str] = [prov_legacy]
    else:
        if isinstance(providers_val, list):
            providers = [str(p).strip().lower() for p in providers_val if p is not None]
        else:
            providers = [str(providers_val).strip().lower()]
    # Filtra desconhecidos mantendo ordem
    filtered_providers: List[str] = []
    seen = set()
    for p in providers:
        if p in allowed_providers and p not in seen:
            filtered_providers.append(p)
            seen.add(p)
    # Se usuário informou algo e nada é válido, lançar erro de validação
    if providers and not filtered_providers:
        raise ConfigValidationError(
            f"Provider(es) ONNX inválido(s): {providers}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.onnx.providers'
        )
    if not filtered_providers:
        filtered_providers = ['cpu']
    # opset (opcional, manter validação)
    try:
        opset = int(onnx.get('opset', 17))
        if opset < 11:
            raise ValueError('opset deve ser >= 11')
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para ai.onnx.opset: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.onnx.opset'
        ) from e
    # Parâmetros opcionais
    model_path = onnx.get('model_path')
    intra_threads = onnx.get('intra_op_num_threads')
    inter_threads = onnx.get('inter_op_num_threads')
    try:
        if intra_threads is not None:
            intra_threads = max(1, int(intra_threads))
        if inter_threads is not None:
            inter_threads = max(1, int(inter_threads))
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para parâmetros de threads em ai.onnx: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.onnx.(intra|inter)_op_num_threads'
        ) from e
    merged['onnx'] = {
        'enabled': onnx_enabled,
        'providers': filtered_providers,
        'provider': filtered_providers[0],
        'opset': opset,
        'model_path': model_path,
        'intra_op_num_threads': intra_threads,
        'inter_op_num_threads': inter_threads,
    }

    # cache
    cache = merged.get('cache', {}) or {}
    cache_enabled = bool(cache.get('enabled', True))
    cache_dir = str(cache.get('dir', 'cache/embeddings')).strip()
    try:
        cache_path = Path(cache_dir)
        if not cache_path.is_absolute():
            cache_path = Path.cwd() / cache_path
        cache_path.mkdir(parents=True, exist_ok=True)
        if not os.access(cache_path, os.W_OK):
            raise PermissionError(f"Sem permissão de escrita em {cache_path}")
    except Exception as e:
        raise ConfigValidationError(
            f"Falha ao preparar diretório de cache: {e}",
            ErrorCode.OUTPUT_WRITE_ERROR,
            'ai.cache.dir'
        ) from e
    try:
        ttl_days = int(cache.get('ttl_days', 30))
        if ttl_days < 0:
            raise ValueError('ttl_days deve ser >= 0')
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido para ai.cache.ttl_days: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.cache.ttl_days'
        ) from e

    merged['cache'] = {
        'enabled': cache_enabled,
        'dir': str(cache_path.absolute()),
        'ttl_days': ttl_days,
    }

    # embeddings (fase 1)
    embeddings = merged.get('embeddings', {}) or {}
    try:
        backend = str(embeddings.get('backend', 'hashing')).strip().lower()
        # Fase 1 suporta apenas 'hashing'
        if backend not in {'hashing'}:
            backend = 'hashing'
        dim = int(embeddings.get('dim', 256))
        if dim < 1:
            raise ValueError('embeddings.dim deve ser >= 1')
        lru_capacity = int(embeddings.get('lru_capacity', 10000))
        if lru_capacity < 1:
            raise ValueError('embeddings.lru_capacity deve ser >= 1')
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(
            f"Valor inválido em ai.embeddings: {e}",
            ErrorCode.CONFIG_VALIDATION_ERROR,
            'ai.embeddings'
        ) from e

    merged['embeddings'] = {
        'backend': backend,
        'dim': dim,
        'lru_capacity': lru_capacity,
    }

    return merged
