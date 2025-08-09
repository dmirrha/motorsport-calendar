"""
Testes de regressão para validação de configuração.

Este módulo contém testes que validam o carregamento e processamento
do arquivo de configuração do sistema.
"""
import os
import json
import pytest
from pathlib import Path
from datetime import datetime

# Configuração para os testes
TEST_CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
SAMPLE_CONFIG = TEST_CONFIG_DIR / "config.json"

class TestConfigValidation:
    """Testes de validação do arquivo de configuração."""
    
    def test_config_file_exists(self):
        """Verifica se o arquivo de configuração existe."""
        assert SAMPLE_CONFIG.exists(), f"Arquivo de configuração não encontrado em {SAMPLE_CONFIG}"
    
    def test_config_is_valid_json(self):
        """Verifica se o arquivo de configuração é um JSON válido."""
        try:
            with open(SAMPLE_CONFIG, 'r', encoding='utf-8') as f:
                config = json.load(f)
            assert isinstance(config, dict), "O arquivo de configuração deve ser um objeto JSON"
        except json.JSONDecodeError as e:
            pytest.fail(f"Erro ao decodificar JSON: {e}")
    
    def test_required_config_sections(self):
        """Verifica se todas as seções obrigatórias estão presentes."""
        with open(SAMPLE_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_sections = [
            'sources', 'output', 'logging', 'retry', 'ui', 
            'calendar', 'filters', 'event_processing'
        ]
        
        for section in required_sections:
            assert section in config, f"Seção obrigatória '{section}' não encontrada na configuração"
    
    def test_logging_config(self):
        """Valida a configuração de logging."""
        with open(SAMPLE_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logging_config = config.get('logging', {})
        
        # Verifica configurações obrigatórias
        assert 'level' in logging_config, "Nível de log não especificado"
        assert logging_config['level'] in [
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ], f"Nível de log inválido: {logging_config['level']}"
        
        # Verifica configurações de rotação de logs
        assert 'max_size_mb' in logging_config, "Tamanho máximo do log não especificado"
        assert isinstance(logging_config['max_size_mb'], (int, float)), "Tamanho máximo do log deve ser um número"
        assert logging_config['max_size_mb'] > 0, "Tamanho máximo do log deve ser maior que zero"
        
        assert 'backup_count' in logging_config, "Número de backups não especificado"
        assert isinstance(logging_config['backup_count'], int), "Número de backups deve ser um inteiro"
        assert logging_config['backup_count'] >= 0, "Número de backups não pode ser negativo"
    
    def test_sources_config(self):
        """Valida a configuração das fontes de dados."""
        with open(SAMPLE_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sources = config.get('sources', [])
        assert isinstance(sources, list), "As fontes devem ser uma lista"
        
        for source in sources:
            assert 'name' in source, "Nome da fonte não especificado"
            assert 'enabled' in source, f"Status de ativação não especificado para a fonte {source.get('name')}"
            
            # Verifica configurações específicas de cada fonte
            if source.get('name') == 'tomada_tempo':
                self._validate_tomada_tempo_config(source)
            # Adicione validações para outras fontes conforme necessário
    
    def _validate_tomada_tempo_config(self, source_config):
        """Valida a configuração específica da fonte Tomada de Tempo."""
        required_fields = [
            'base_url', 'endpoints', 'timeout', 'retry_attempts'
        ]
        
        for field in required_fields:
            assert field in source_config, f"Campo obrigatório '{field}' não encontrado na configuração da fonte Tomada de Tempo"
        
        # Valida endpoints obrigatórios
        endpoints = source_config.get('endpoints', {})
        required_endpoints = [
            'programacao', 'evento', 'categorias'
        ]
        
        for endpoint in required_endpoints:
            assert endpoint in endpoints, f"Endpoint obrigatório '{endpoint}' não encontrado na configuração da fonte Tomada de Tempo"
