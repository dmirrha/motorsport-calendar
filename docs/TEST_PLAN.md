# TEST_PLAN

## 2.1.1 Extração e Filtragem (TomadaTempo)

- Correção 2025-08-08: Tornar determinístico `tests/test_tomada_tempo.py::test_filter_weekend_events`.
  - Antes: intervalo do fim de semana calculado com base em `datetime.now()` via `_get_next_weekend()`.
  - Depois: intervalo ancorado na própria data do evento de teste (`01/08/2025`, America/Sao_Paulo).
  - Impacto: elimina flakiness em execuções locais e no CI.
  - Validação: suíte completa passou localmente (37/37) após a correção.

### Notas
- Método de produção utilizado: `sources/base_source.py::filter_weekend_events()` (sem alterações funcionais nesta correção).
- O teste agora usa `BaseSource.parse_date_time()` para garantir timezone-aware e precisão do range do FDS.

### Próximos passos
- Aumentar cobertura dos módulos críticos (`sources/tomada_tempo.py`, `event_processor.py`).
- Adicionar casos para AM/PM, datas por extenso e eventos overnight (vide prioridades em TESTING_STANDARDS e plano de qualidade).
