#!/usr/bin/env python3
"""
Debug script para analisar a filtragem de eventos do fim de semana
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sources.tomada_tempo import TomadaTempoSource

def debug_weekend_filtering():
    """Debug da filtragem de eventos do fim de semana."""
    
    # Criar instância da fonte
    source = TomadaTempoSource()
    
    # Eventos de teste
    test_events = [
        {
            'name': 'F1 Test Event',
            'date': '01/08/2025',
            'time': '16:30',
            'category': 'F1',
            'location': 'Interlagos'
        },
        {
            'name': 'NASCAR Test Event', 
            'date': '02/08/2025',
            'time': '14:00',
            'category': 'NASCAR',
            'location': 'Tarumã'
        },
        {
            'name': 'MotoGP Test Event',
            'date': '10/08/2025',  # Data futura (domingo)
            'time': '15:00',
            'category': 'MotoGP',
            'location': 'Mônaco'
        }
    ]
    
    print("=== DEBUG: FILTRAGEM DE EVENTOS DO FIM DE SEMANA ===")
    print(f"Data atual: {datetime.now()}")
    print(f"Weekday atual: {datetime.now().weekday()} (0=Segunda, 6=Domingo)")
    print()
    
    # Debug do método _get_next_weekend
    current_weekend_friday = source._get_next_weekend()
    print(f"Sexta-feira do fim de semana atual: {current_weekend_friday}")
    print(f"Weekday da sexta: {current_weekend_friday.weekday()}")
    print()
    
    # Debug de cada evento
    print("=== ANÁLISE DOS EVENTOS ===")
    for i, event in enumerate(test_events):
        print(f"\nEvento {i+1}: {event['name']}")
        print(f"  Data original: {event['date']}")
        
        # Tentar fazer o parsing da data
        try:
            parsed_date = source.parse_date_time(event['date'])
            if parsed_date:
                print(f"  Data parseada: {parsed_date}")
                print(f"  Weekday: {parsed_date.weekday()} ({'Sexta' if parsed_date.weekday() == 4 else 'Sábado' if parsed_date.weekday() == 5 else 'Domingo' if parsed_date.weekday() == 6 else 'Outro dia'})")
                print(f"  É fim de semana (>=4)? {parsed_date.weekday() >= 4}")
            else:
                print(f"  ERRO: Não foi possível fazer o parsing da data")
        except Exception as e:
            print(f"  ERRO no parsing: {e}")
    
    print("\n=== TESTE DE FILTRAGEM ===")
    
    # Testar filtragem
    try:
        weekend_events = source.filter_weekend_events(test_events)
        print(f"Eventos filtrados: {len(weekend_events)}")
        
        for i, event in enumerate(weekend_events):
            print(f"  {i+1}. {event['name']} - {event['date']}")
            
        print(f"\nEventos excluídos: {len(test_events) - len(weekend_events)}")
        
        for event in test_events:
            if event not in weekend_events:
                print(f"  - {event['name']} - {event['date']}")
                
    except Exception as e:
        print(f"ERRO na filtragem: {e}")
        
    print("\n=== TESTE COM RANGE DE DATAS ===")
    
    # Testar com range específico do fim de semana
    try:
        import pytz
        tz = pytz.timezone('America/Sao_Paulo')
        
        # Ensure current_weekend_friday has timezone
        if current_weekend_friday.tzinfo is None:
            current_weekend_friday = tz.localize(current_weekend_friday)
            
        weekend_start = current_weekend_friday.replace(hour=0, minute=0, second=0, microsecond=0)
        weekend_end = weekend_start + timedelta(days=2, hours=23, minutes=59, seconds=59)
        
        print(f"Range do fim de semana:")
        print(f"  Início: {weekend_start}")
        print(f"  Fim: {weekend_end}")
        print(f"  Timezone do range: {weekend_start.tzinfo}")
        
        # Debug detalhado de cada evento vs range
        print("\n--- DEBUG DETALHADO DE COMPARAÇÃO ---")
        for i, event in enumerate(test_events):
            print(f"\nEvento {i+1}: {event['name']}")
            try:
                parsed_date = source.parse_date_time(event['date'])
                if parsed_date:
                    print(f"  Data parseada: {parsed_date}")
                    print(f"  Timezone: {parsed_date.tzinfo}")
                    print(f"  Data >= início? {parsed_date >= weekend_start}")
                    print(f"  Data <= fim? {parsed_date <= weekend_end}")
                    print(f"  Dentro do range? {weekend_start <= parsed_date <= weekend_end}")
                else:
                    print(f"  ERRO: Não foi possível parsear a data")
            except Exception as e:
                print(f"  ERRO no parsing: {e}")
        
        weekend_events_with_range = source.filter_weekend_events(test_events, (weekend_start, weekend_end))
        print(f"\nEventos filtrados com range: {len(weekend_events_with_range)}")
        
        for i, event in enumerate(weekend_events_with_range):
            print(f"  {i+1}. {event['name']} - {event['date']}")
            
    except Exception as e:
        print(f"ERRO na filtragem com range: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== TESTE SIMULANDO collect_events ===")
    
    # Simular exatamente o que o collect_events faz
    try:
        import pytz
        tz = pytz.timezone('America/Sao_Paulo')
        
        target_date = source._get_next_weekend()
        
        # Ensure target_date has timezone (como no collect_events)
        if target_date.tzinfo is None:
            target_date = tz.localize(target_date)
        
        weekend_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        weekend_end = weekend_start + timedelta(days=2, hours=23, minutes=59, seconds=59)
        target_weekend = (weekend_start, weekend_end)
        
        print(f"Simulação collect_events:")
        print(f"  target_date: {target_date}")
        print(f"  weekend_start: {weekend_start}")
        print(f"  weekend_end: {weekend_end}")
        
        filtered_events = source.filter_weekend_events(test_events, target_weekend)
        print(f"\nEventos filtrados (simulação): {len(filtered_events)}")
        
        for i, event in enumerate(filtered_events):
            print(f"  {i+1}. {event['name']} - {event['date']}")
            
    except Exception as e:
        print(f"ERRO na simulação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_weekend_filtering()
