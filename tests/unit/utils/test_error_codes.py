import pytest

from src.utils.error_codes import (
    ErrorCode,
    get_error_suggestions,
    get_error_severity,
)


def test_get_error_suggestions_known_codes():
    assert "JSON válido" in get_error_suggestions(ErrorCode.CONFIG_INVALID_JSON)
    assert "permissões de escrita" in get_error_suggestions(ErrorCode.LOG_FILE_WRITE_ERROR)
    assert "Muitas requisições" in get_error_suggestions(ErrorCode.SOURCE_RATE_LIMIT)
    assert "critérios de validação" in get_error_suggestions(ErrorCode.PROCESSOR_VALIDATION_ERROR)
    assert "Permissão negada" in get_error_suggestions(ErrorCode.OUTPUT_PERMISSION_ERROR)
    assert "erro inesperado" in get_error_suggestions(ErrorCode.SYSTEM_UNEXPECTED)


def test_get_error_suggestions_fallback_for_known_code_without_mapping():
    # Código existente, mas sem sugestão específica no dicionário -> fallback genérico
    msg = get_error_suggestions(ErrorCode.CONFIG_MISSING_REQUIRED)
    assert "Consulte a documentação" in msg


def test_get_error_suggestions_fallback_for_unknown_string_code():
    # Código não mapeado e enviado como string -> fallback genérico
    msg = get_error_suggestions("FOO-0000-ERROR")  # type: ignore[arg-type]
    assert "Consulte a documentação" in msg


def test_get_error_severity_known_cases_with_enum():
    assert get_error_severity(ErrorCode.LOGGER_INIT_FAILED) == "CRITICAL"
    assert get_error_severity(ErrorCode.SOURCE_RATE_LIMIT) == "WARNING"
    assert get_error_severity(ErrorCode.SYSTEM_RESOURCE_LIMIT) == "ERROR"


def test_get_error_severity_with_string_and_enum_equivalence():
    code = ErrorCode.OUTPUT_FORMAT_ERROR
    # str(enum) retorna 'ErrorCode.OUTPUT_FORMAT_ERROR'. Use o valor literal do código.
    assert get_error_severity(code) == get_error_severity(code.value)


@pytest.mark.parametrize("value", [None, "", "FOO", "A-B"])  # type: ignore[list-item]
def test_get_error_severity_invalid_inputs_return_unknown(value):
    # type: ignore[arg-type]
    assert get_error_severity(value) == "UNKNOWN"
