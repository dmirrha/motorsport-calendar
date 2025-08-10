"""
Testes unitários para o módulo config_validator.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path para permitir imports absolutos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config_validator import (
    validate_logging_config,
    validate_payload_settings,
    validate_silent_periods,
    ConfigValidationError
)
from src.utils.error_codes import ErrorCode


class TestConfigValidator(unittest.TestCase):
    """Testes para as funções de validação de configuração."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.test_dir = Path(self.temp_dir.name)
        
        # Cria diretórios de teste
        (self.test_dir / 'logs').mkdir(exist_ok=True)
        (self.test_dir / 'logs' / 'debug').mkdir(exist_ok=True)
        (self.test_dir / 'logs' / 'payloads').mkdir(exist_ok=True)
        
        # Configuração de exemplo
        self.valid_config = {
            'file_structure': {
                'main_log': str(self.test_dir / 'logs' / 'app.log'),
                'debug_directory': str(self.test_dir / 'logs' / 'debug'),
                'payload_directory': str(self.test_dir / 'logs' / 'payloads')
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
                'console': '%(message)s',
                'file': '%(asctime)s - %(message)s'
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
    
    def test_validate_logging_config_valid(self):
        """Testa a validação de uma configuração de logging válida."""
        result = validate_logging_config(self.valid_config)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['levels']['console'], 'INFO')
        self.assertEqual(result['retention']['max_logs_to_keep'], 10)
        self.assertTrue(Path(result['file_structure']['main_log']).is_absolute())
    
    def test_validate_logging_config_missing_required(self):
        """Testa a validação com configuração ausente."""
        with self.assertRaises(ConfigValidationError) as cm:
            validate_logging_config({})
        self.assertEqual(cm.exception.error_code, ErrorCode.CONFIG_MISSING_REQUIRED)
    
    def test_validate_logging_config_invalid_log_level(self):
        """Testa a validação com nível de log inválido."""
        invalid_config = self.valid_config.copy()
        invalid_config['levels']['console'] = 'INVALID_LEVEL'
        
        with self.assertRaises(ConfigValidationError) as cm:
            validate_logging_config(invalid_config)
        self.assertEqual(cm.exception.error_code, ErrorCode.CONFIG_VALIDATION_ERROR)
    
    @patch('os.access', return_value=False)
    def test_validate_logging_config_permission_error(self, mock_access):
        """Testa tratamento de erro de permissão em diretório."""
        with self.assertRaises(ConfigValidationError) as cm:
            validate_logging_config(self.valid_config)
        self.assertEqual(cm.exception.error_code, ErrorCode.OUTPUT_WRITE_ERROR)
    
    def test_validate_payload_settings_defaults(self):
        """Testa a validação com configurações padrão."""
        result = validate_payload_settings({})
        self.assertTrue(result['save_raw'])
        self.assertTrue(result['pretty_print'])
        self.assertEqual(result['max_files_per_source'], 50)
    
    def test_validate_payload_settings_custom_values(self):
        """Testa a validação com valores personalizados."""
        custom_settings = {
            'save_raw': False,
            'max_files_per_source': '100',  # Testa conversão de string para int
            'max_age_days': '90',
            'new_setting': 'value'  # Deve ser mantido
        }
        result = validate_payload_settings(custom_settings)
        self.assertFalse(result['save_raw'])
        self.assertEqual(result['max_files_per_source'], 100)
        self.assertEqual(result['max_age_days'], 90)
        self.assertEqual(result['new_setting'], 'value')
    
    def test_validate_payload_settings_invalid_numeric(self):
        """Testa a validação com valores numéricos inválidos."""
        with self.assertRaises(ConfigValidationError) as cm:
            validate_payload_settings({'max_files_per_source': 'invalid'})
        self.assertEqual(cm.exception.error_code, ErrorCode.CONFIG_VALIDATION_ERROR)
    
    def test_validate_silent_periods_valid(self):
        """Testa a validação de períodos de silêncio válidos."""
        periods = [
            {
                'name': 'Noite',
                'start_time': '22:00',
                'end_time': '06:00',
                'days_of_week': ['monday', 'tuesday', 'wednesday', 'thursday', 'sunday'],
                'enabled': True
            },
            {
                'name': 'Fim de semana',
                'start_time': '00:00',
                'end_time': '23:59',
                'days_of_week': ['saturday', 'sunday']
                # enabled omitido, deve ser True por padrão
            }
        ]
        
        result = validate_silent_periods(periods)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Noite')
        self.assertEqual(result[0]['start_time'], '22:00')
        # Ordena os dias da semana para comparar sem depender da ordem
        self.assertEqual(sorted(result[1]['days_of_week']), sorted(['saturday', 'sunday']))
        self.assertTrue(result[1]['enabled'])  # Valor padrão
    
    def test_validate_silent_periods_invalid_time_format(self):
        """Testa a validação com formato de hora inválido."""
        periods = [{
            'name': 'Período inválido',
            'start_time': '25:00',  # Hora inválida
            'end_time': '08:00',
            'days_of_week': ['monday']
        }]
        
        # A função não deve levantar exceção, mas sim registrar um erro
        with patch('logging.Logger.error') as mock_error:
            result = validate_silent_periods(periods)
            self.assertEqual(len(result), 0)  # Nenhum período válido retornado
            mock_error.assert_called()
    
    def test_validate_silent_periods_missing_required_field(self):
        """Testa a validação com campo obrigatório ausente."""
        periods = [{
            'name': 'Período incompleto',
            'start_time': '22:00',
            # end_time ausente
            'days_of_week': ['monday']
        }]
        
        # A função não deve levantar exceção, mas sim registrar um erro
        with patch('logging.Logger.error') as mock_error:
            result = validate_silent_periods(periods)
            self.assertEqual(len(result), 0)  # Nenhum período válido retornado
            mock_error.assert_called()
    
    def test_validate_silent_periods_invalid_structure(self):
        """Testa a validação com estrutura inválida."""
        # Não é uma lista
        result = validate_silent_periods({"not": "a list"})
        self.assertEqual(result, [])
        
        # Item não é um dicionário
        result = validate_silent_periods(["not a dict"])
        self.assertEqual(len(result), 0)
    
    def test_validate_silent_periods_invalid_weekday(self):
        """Testa a validação com dias da semana inválidos."""
        periods = [{
            'name': 'Período com dias inválidos',
            'start_time': '22:00',
            'end_time': '06:00',
            'days_of_week': ['segunda', 'terça', 'monday']  # Apenas 'monday' é válido
        }]
        
        # A função não deve registrar warnings para dias inválidos, apenas para quando não há dias válidos
        result = validate_silent_periods(periods)
        
        # Verifica que o período foi incluído com apenas os dias válidos
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['days_of_week'], ['monday'])
        
        # Verifica que o período está habilitado por padrão
        self.assertTrue(result[0]['enabled'])
        
        # Verifica que os horários foram mantidos corretamente
        self.assertEqual(result[0]['start_time'], '22:00')
        self.assertEqual(result[0]['end_time'], '06:00')
    
    def test_validate_silent_periods_no_weekdays(self):
        """Testa a validação sem dias da semana especificados."""
        periods = [{
            'name': 'Sem dias',
            'start_time': '00:00',
            'end_time': '23:59',
            'days_of_week': []  # Lista vazia
        }]
        
        with patch('logging.Logger.warning') as mock_warning:
            result = validate_silent_periods(periods)
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]['days_of_week']), 7)  # Deve usar todos os dias
            mock_warning.assert_called()


if __name__ == '__main__':
    unittest.main()
