"""
Testes de regressão para geração de arquivos iCal.

Este módulo contém testes que validam a geração correta
dos arquivos iCal a partir dos eventos coletados.
"""
import os
import json
import pytest
import icalendar
from pathlib import Path
from datetime import datetime, timedelta

# Configuração para os testes
TEST_CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
TEST_DATA_DIR = Path(__file__).parent / "test_data"
SAMPLE_CONFIG = TEST_CONFIG_DIR / "config.json"

class TestICalGeneration:
    """Testes para geração de arquivos iCal."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Configuração e limpeza para cada teste."""
        # Cria diretório temporário para saída dos testes
        self.output_dir = TEST_DATA_DIR / "output" / f"test_ical_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Carrega a configuração de teste
        with open(SAMPLE_CONFIG, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Modifica a configuração para usar diretórios de teste
        self.config['output']['directory'] = str(self.output_dir)
        self.config['calendar']['filename'] = 'test_calendar.ics'
        
        # Salva a configuração modificada temporariamente
        self.temp_config_path = self.output_dir / "test_config.json"
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        
        yield  # Executa o teste
        
        # Limpeza após o teste
        # (opcional - mantém os arquivos para depuração)
    
    def test_ical_file_generation(self):
        """Testa a geração do arquivo iCal a partir dos eventos coletados."""
        from src.motorsport_calendar import MotorsportCalendar
        from src.utils.ical_generator import generate_ical
        
        # Cria eventos de teste
        test_events = [
            {
                'title': 'Evento de Teste 1',
                'start_datetime': datetime.now() + timedelta(days=1),
                'end_datetime': datetime.now() + timedelta(days=1, hours=2),
                'description': 'Descrição do evento de teste 1',
                'location': 'Local de Teste',
                'category': 'F1',
                'source': 'test_source',
                'url': 'https://example.com/event1'
            },
            {
                'title': 'Evento de Teste 2',
                'start_datetime': datetime.now() + timedelta(days=2),
                'end_datetime': datetime.now() + timedelta(days=2, hours=3),
                'description': 'Descrição do evento de teste 2',
                'location': 'Outro Local de Teste',
                'category': 'IndyCar',
                'source': 'test_source',
                'url': 'https://example.com/event2'
            }
        ]
        
        # Gera o arquivo iCal
        ical_file = self.output_dir / self.config['calendar']['filename']
        generate_ical(test_events, str(ical_file))
        
        # Verifica se o arquivo foi criado
        assert ical_file.exists(), "Arquivo iCal não foi gerado"
        
        # Verifica o conteúdo do arquivo
        with open(ical_file, 'rb') as f:
            calendar = icalendar.Calendar.from_ical(f.read())
            
            # Verifica metadados do calendário
            assert calendar.get('prodid') == '-//Motorsport Calendar//motorsport-calendar//', \
                "PRODID do calendário incorreto"
            assert 'VEVENT' in calendar, "Nenhum evento encontrado no calendário"
            
            # Verifica os eventos
            events = [comp for comp in calendar.walk() if comp.name == 'VEVENT']
            assert len(events) == len(test_events), "Número incorreto de eventos no calendário"
            
            # Verifica os detalhes de cada evento
            for i, event in enumerate(events):
                test_event = test_events[i]
                
                # Verifica campos básicos
                assert str(event.get('summary')) == test_event['title'], f"Título incorreto para evento {i+1}"
                assert str(event.get('description')).startswith(test_event['description']), f"Descrição incorreta para evento {i+1}"
                assert str(event.get('location')) == test_event['location'], f"Local incorreto para evento {i+1}"
                assert str(event.get('url')) == test_event['url'], f"URL incorreta para evento {i+1}"
                
                # Verifica datas
                start_dt = event.get('dtstart').dt
                assert start_dt == test_event['start_datetime'].replace(tzinfo=start_dt.tzinfo), \
                    f"Data de início incorreta para evento {i+1}"
                
                end_dt = event.get('dtend').dt
                assert end_dt == test_event['end_datetime'].replace(tzinfo=end_dt.tzinfo), \
                    f"Data de término incorreta para evento {i+1}"
                
                # Verifica categorias
                categories = event.get('categories')
                assert categories is not None, f"Categoria não definida para evento {i+1}"
                assert str(categories.cats[0]) == test_event['category'], f"Categoria incorreta para evento {i+1}"
    
    def test_ical_generation_with_missing_fields(self):
        """Testa a geração de iCal com eventos que possuem campos opcionais ausentes."""
        from src.utils.ical_generator import generate_ical
        
        # Evento com campos mínimos
        minimal_event = {
            'title': 'Evento Mínimo',
            'start_datetime': datetime.now() + timedelta(days=1),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'category': 'F1',
            'source': 'test_source',
            'url': 'https://example.com/minimal'
        }
        
        # Gera o arquivo iCal
        ical_file = self.output_dir / "minimal_calendar.ics"
        generate_ical([minimal_event], str(ical_file))
        
        # Verifica se o arquivo foi criado
        assert ical_file.exists(), "Arquivo iCal não foi gerado"
        
        # Verifica o conteúdo do arquivo
        with open(ical_file, 'rb') as f:
            calendar = icalendar.Calendar.from_ical(f.read())
            events = [comp for comp in calendar.walk() if comp.name == 'VEVENT']
            assert len(events) == 1, "Deve haver exatamente um evento no calendário"
            
            event = events[0]
            assert str(event.get('summary')) == minimal_event['title']
            assert event.get('description') is None, "Descrição deveria ser opcional"
            assert event.get('location') is None, "Local deveria ser opcional"
    
    def test_ical_generation_with_recurring_events(self):
        """Testa a geração de iCal com eventos recorrentes."""
        from src.utils.ical_generator import generate_ical
        
        # Cria um evento recorrente (a cada semana por 4 semanas)
        start_date = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        recurring_event = {
            'title': 'Treino Livre - F1',
            'start_datetime': start_date,
            'end_datetime': start_date + timedelta(hours=1.5),
            'description': 'Sessão de treino livre',
            'location': 'Circuito de Teste',
            'category': 'F1',
            'source': 'test_source',
            'url': 'https://example.com/recurring',
            'recurrence': {
                'freq': 'WEEKLY',
                'count': 4
            }
        }
        
        # Gera o arquivo iCal
        ical_file = self.output_dir / "recurring_calendar.ics"
        generate_ical([recurring_event], str(ical_file))
        
        # Verifica se o arquivo foi criado
        assert ical_file.exists(), "Arquivo iCal não foi gerado"
        
        # Verifica o conteúdo do arquivo
        with open(ical_file, 'rb') as f:
            calendar = icalendar.Calendar.from_ical(f.read())
            events = [comp for comp in calendar.walk() if comp.name == 'VEVENT']
            
            # Verifica se há pelo menos um evento recorrente
            assert len(events) > 0, "Nenhum evento encontrado no calendário"
            
            # Verifica se o primeiro evento tem a regra de recorrência
            event = events[0]
            rrule = event.get('rrule')
            assert rrule is not None, "Evento recorrente não tem regra de recorrência"
            assert 'FREQ=WEEKLY' in str(rrule), "Frequência de recorrência incorreta"
            assert 'COUNT=4' in str(rrule), "Contagem de recorrência incorreta"
