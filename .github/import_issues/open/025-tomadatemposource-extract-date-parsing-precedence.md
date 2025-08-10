# Bug: Precedência de parsing ISO vs BR em TomadaTempoSource._extract_date()

## 📝 Descrição
Atualmente, `TomadaTempoSource._extract_date()` parece priorizar subcapturas no formato BR ao processar strings que estão no formato ISO (`YYYY-MM-DD`). Isso causa interpretação incorreta de datas ISO como se fossem BR (ex.: `2025-08-02` pode ser parcialmente interpretado como `02-08-2025` via subcapturas), dependendo da ordem e sobreposição das regex.

## 🔍 Contexto
- Arquivo: `sources/tomada_tempo.py`
- Função: `_extract_date()`
- Teste relacionado: `tests/unit/sources/tomada_tempo/test_parsing_core.py` (caso de data ISO)
- Situação atual: o teste foi ajustado temporariamente para refletir a precedência vigente do parser. O comportamento desejado é priorizar o formato ISO quando a string corresponder claramente a `YYYY-MM-DD`.

## 🎯 Comportamento Esperado
- Quando a entrada corresponder ao padrão ISO completo (`^\d{4}-\d{2}-\d{2}$`), a função deve parsear como ISO, sem permitir que subcapturas para formato BR tenham precedência.
- Manter compatibilidade com formatos BR e demais variações já suportadas.

## 🛠️ Passos para Reproduzir
1. Preparar entrada de data como string: `"2025-08-02"`.
2. Invocar a lógica de extração de data (via caminho exercitado nos testes de parsing do Tomada de Tempo).
3. Observar que a interpretação pode seguir a via de subcapturas BR em vez de priorizar ISO.

## 📱 Ambiente
- SO: macOS
- Versão: desenvolvimento (branchs de Fase 1.1)

## 📋 Tarefas
- [ ] Analisar `_extract_date()` e mapear a ordem/competição das regex
- [ ] Priorizar regex ISO antes de subcapturas BR quando a entrada for ISO válida
- [ ] Restaurar o teste de ISO para validar o comportamento esperado
- [ ] Adicionar casos paramétricos (ISO puro, ISO com horários, ruídos comuns)
- [ ] Atualizar documentação (`tests/README.md` e notas no `CHANGELOG.md`)
- [ ] Registrar cobertura e tempo de execução pós-ajuste

## 📊 Impacto
Médio — O parsing de datas é central para construção de cronogramas. Ambiguidades podem afetar associatividade de eventos e consistência de calendário.
