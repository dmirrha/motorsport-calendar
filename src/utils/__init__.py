"""
Módulo de utilitários para o Motorsport Calendar.

Este pacote contém utilitários compartilhados usados em todo o projeto,
incluindo manipulação de erros, validação de configuração e gerenciamento de payloads.
"""

# Importações dos módulos do pacote
from .error_codes import ErrorCode, get_error_suggestions, get_error_severity
from .config_validator import validate_logging_config, validate_payload_settings, validate_silent_periods, ConfigValidationError
from .payload_manager import PayloadManager
from .anomaly_detector import AnomalyDetector, AnomalyConfig

__all__ = [
    'ErrorCode',
    'get_error_suggestions',
    'get_error_severity',
    'validate_logging_config',
    'validate_payload_settings',
    'validate_silent_periods',
    'ConfigValidationError',
    'PayloadManager',
    'AnomalyDetector',
    'AnomalyConfig'
]
