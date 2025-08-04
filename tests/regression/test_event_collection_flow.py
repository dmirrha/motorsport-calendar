"""
Testes de regressão para o fluxo de coleta de eventos.

Este módulo contém testes que validam o fluxo completo de coleta
e processamento de eventos a partir das fontes configuradas.
"""
import os
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta

# Configuração para os testes
TEST_CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
TEST_DATA_DIR = Path(__file__).parent / "test_data"
SAMPLE_CONFIG = TEST_CONFIG_DIR / "config.json"

# Cria diretório de dados de teste se não existir
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

class TestEventCollectionFlow:
    """Testes para o fluxo de coleta de eventos."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Configuração e limpeza para cada teste."""
        # Cria diretório temporário para saída dos testes
        self.output_dir = TEST_DATA_DIR / "output" / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Carrega a configuração de teste
        with open(SAMPLE_CONFIG, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Modifica a configuração para usar diretórios de teste
        self.config['output']['directory'] = str(self.output_dir)
        self.config['logging']['level'] = 'DEBUG'
        
        # Salva a configuração modificada temporariamente
        self.temp_config_path = self.output_dir / "test_config.json"
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        
        yield  # Executa o teste
        
        # Limpeza após o teste (opcional)
        # Pode ser usado para limpar arquivos temporários se necessário
    
    def test_event_collection_process(self):
        """Testa o processo completo de coleta de eventos."""
        from src.motorsport_calendar import MotorsportCalendar
        
        # Inicializa o coletor com a configuração de teste
        calendar = MotorsportCalendar(config_path=str(self.temp_config_path))
        
        # Executa a coleta de eventos
        events = calendar.collect_events()
        
        # Verificações básicas
        assert isinstance(events, list), "A lista de eventos deve ser uma lista"
        
        # Verifica se os eventos foram processados corretamente
        if events:  # Se houver eventos
            for event in events:
                self._validate_event_structure(event)
        
        # Verifica se os arquivos de saída foram gerados
        output_files = list(self.output_dir.glob("*.ics"))
        assert len(output_files) > 0, "Nenhum arquivo .ics foi gerado"
        
        # Verifica se o arquivo de log foi criado
        log_files = list(self.output_dir.glob("*.log"))
        assert len(log_files) > 0, "Nenhum arquivo de log foi gerado"
        
        # Verifica o conteúdo do arquivo de log para erros
        self._check_log_for_errors(log_files[0])
    
    def _validate_event_structure(self, event):
        """Valida a estrutura de um evento."""
        required_fields = [
            'title', 'start_datetime', 'end_datetime', 
            'category', 'source', 'url'
        ]
        
        for field in required_fields:
            assert field in event, f"Campo obrigatório '{field}' não encontrado no evento"
        
        # Validação de tipos
        assert isinstance(event['title'], str), "O título do evento deve ser uma string"
        assert isinstance(event['start_datetime'], (str, datetime)), "A data de início deve ser uma string ou datetime"
        assert isinstance(event['end_datetime'], (str, datetime, type(None))), "A data de término deve ser uma string, datetime ou None"
        assert isinstance(event['category'], str), "A categoria deve ser uma string"
        assert isinstance(event['source'], str), "A fonte deve ser uma string"
        
        # Validação de datas
        if isinstance(event['start_datetime'], str):
            try:
                datetime.fromisoformat(event['start_datetime'].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"Formato de data de início inválido: {event['start_datetime']}")
        
        if event['end_datetime'] and isinstance(event['end_datetime'], str):
            try:
                end_dt = datetime.fromisoformat(event['end_datetime'].replace('Z', '+00:00'))
                start_dt = datetime.fromisoformat(event['start_datetime'].replace('Z', '+00:00'))
                assert end_dt > start_dt, "A data de término deve ser posterior à data de início"
            except ValueError:
                pytest.fail(f"Formato de data de término inválido: {event['end_datetime']}")
    
    def _check_log_for_errors(self, log_file):
        """Verifica o arquivo de log em busca de erros."""
        error_keywords = [
            'ERROR', 'CRITICAL', 'Exception', 'Traceback',
            'falha', 'erro', 'timeout', 'conexão recusada'
        ]
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                
            errors_found = []
            for keyword in error_keywords:
                if keyword.lower() in log_content.lower():
                    errors_found.append(keyword)
            
            if errors_found:
                error_msg = f"Foram encontradas as seguintes palavras-chave de erro no log: {', '.join(errors_found)}"
                pytest.fail(error_msg)
                
        except Exception as e:
            pytest.fail(f"Erro ao verificar o arquivo de log: {e}")

    @pytest.mark.parametrize("days_ahead", [1, 7, 30])
    def test_event_filtering_by_date_range(self, days_ahead):
        """Testa a filtragem de eventos por intervalo de datas."""
        from src.motorsport_calendar import MotorsportCalendar
        
        # Configura datas para teste
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Modifica a configuração para o teste
        self.config['filters']['date_range'] = {
            'enabled': True,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        # Salva a configuração modificada
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        
        # Executa a coleta
        calendar = MotorsportCalendar(config_path=str(self.temp_config_path))
        events = calendar.collect_events()
        
        # Verifica se os eventos estão dentro do intervalo
        for event in events:
            event_date = datetime.fromisoformat(
                event['start_datetime'].replace('Z', '+00:00')
            )
            assert start_date <= event_date <= end_date, \
                f"Evento fora do intervalo de datas: {event['title']} em {event['start_datetime']}"
