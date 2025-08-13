# Issue #75 — Bug: Precedência de parsing ISO vs BR em TomadaTempoSource._extract_date()

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/75
- Arquivo: `sources/tomada_tempo.py`
- Função: `_extract_date()`
- Testes: `tests/unit/sources/tomada_tempo/test_parsing_core.py`, `tests/unit/sources/tomada_tempo/test_extract_date_time_edge_cases.py`

## Objetivo
Corrigir a precedência do parsing de datas para priorizar formatos ISO completos (`YYYY-MM-DD`/`YYYY/MM/DD`) e anos completos em BR, evitando subcapturas parciais de `DD-MM-YY`.

## Causa
A ordem e a ausência de limites/lookarounds nas regex permitiam que strings ISO fossem parcialmente interpretadas como BR (subcapturas), causando datas invertidas.

## Correção aplicada
- Reordenação de precedência em `_extract_date()`:
  1. `DD/MM/YYYY | DD-MM-YYYY` (limites de palavra/lookarounds)
  2. `YYYY/MM/DD | YYYY-MM-DD` (ISO completo) com limites
  3. `DD/MM/YY | DD-MM/YY` como fallback
- Inclusão de lookarounds positivos/negativos para bloquear matches parciais.
- Limpeza em `_extract_time()` removendo placeholder inválido.

## Testes atualizados
- `test_extract_date_time_edge_cases.py`: casos de borda para evitar matches parciais e prioridades de ISO.
- `test_parsing_core.py`: expectativa de ISO com ano completo priorizada.

## Critérios de aceite
- Suíte sem falhas e sem warnings.
- Datas ISO (`^\d{4}-\d{2}-\d{2}$`) interpretadas corretamente.
- BR com ano completo priorizado sobre BR de 2 dígitos.
- Sem matches parciais em strings com ruído.

## Plano de resolução
- [x] Mapear competição de regex e efeito de subcapturas
- [x] Reordenar precedência e adicionar lookarounds
- [x] Atualizar testes e expectativas
- [x] Rodar suíte 3× (zero flakes)
- [x] Registrar rastreio e notas

## Métricas
- Suíte: 205 passed; 3× locais; gate 45% atingido
- Cobertura global: ~61.68%
- Arquivo `sources/tomada_tempo.py`: ~63%

## Comandos
```
git add sources/tomada_tempo.py \
  tests/unit/sources/tomada_tempo/test_extract_date_time_edge_cases.py \
  tests/unit/sources/tomada_tempo/test_parsing_core.py

git commit -m "fix(tomada_tempo): priorizar ISO completo e evitar matches parciais em _extract_date; atualizar testes (#75)"
```
