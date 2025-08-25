# ✨ Aprimorar detecção de categorias de automobilismo

## 📝 Descrição
Ampliar o suporte a categorias de automobilismo para melhor classificação dos eventos coletados do Tomada de Tempo.

## 🔍 Contexto
O projeto atualmente detecta categorias via `CategoryDetector` em `src/category_detector.py` usando normalização e fuzzy matching, com aprendizado dinâmico de variações. A fonte `TomadaTempoSource` em `sources/tomada_tempo.py` extrai títulos, categorias brutas e demais campos. Limitações registradas:
- Dicionário limitado de categorias e variações
- Dificuldade em reconhecer sinônimos/abreviações
- Cobertura fraca de categorias nacionais/regionais
- Observação: possível bug onde alguns títulos no iCal exibem categoria incorreta (`src/ical_generator.py`)

## 🎯 Comportamento Esperado
- Detecção robusta e consistente de categorias (internacionais, nacionais e regionais)
- Suporte a sinônimos/variações e mapeamento para uma forma canônica
- Classificação com precisão mínima de 90% e cobertura de ≥95% do que aparece no Tomada de Tempo
- iCal exibe a categoria correta para cada evento

## 🛠️ Passos para Reproduzir (parciais)
1. Executar coleta/parsing da fonte Tomada de Tempo (tests de integração existentes em `tests/integration/`)
2. Verificar categorias resultantes e o conteúdo gerado no iCal
3. Identificar casos com classificação inadequada ou categoria ausente

## 🧭 Plano de Resolução
1. Expandir e organizar o dicionário de categorias em `src/category_detector.py`:
   - Adicionar internacionais (F1, F2, F3, F1 Academy, WEC, WRC, WRX, IMSA, IndyCar, MotoGP, WSBK, etc.)
   - Adicionar nacionais/regionais (Stock Car, Copa Truck, Fórmula Truck, Turismo Nacional, marcas regionais, kart)
   - Adicionar sinônimos/variações/abreviações comuns (ex.: “F-Indy”, “Prototipos”, “F-Truck”)
2. Introduzir mapeamento de aliases → categoria canônica (ex.: "IMSA WeatherTech" → "IMSA").
3. Melhorar detecção baseada em contexto:
   - Usar título/subtítulo/URL/segmentos de página (quando disponíveis) como boosters de score
   - Estratégia: scoring adicional para termos de alta confiança no título e no slug da categoria
4. Ajustar `TomadaTempoSource` para passar contexto adicional ao `CategoryDetector` (sem quebrar compatibilidade).
5. Revisitar formatação de título/descrição no `ICalGenerator` para garantir exibição coerente da categoria.
6. Criar/atualizar testes:
   - Unit: `src/category_detector.py` cobrindo novas categorias, sinônimos e contexto
   - Integração: `sources/tomada_tempo.py` garantindo classificação correta em cenários reais (fixtures)
   - Verificação: iCal apresenta categoria correta
7. Documentação:
   - Atualizar `DATA_SOURCES.md` e `README.md` com lista/estratégia de categorias
   - Atualizar `CHANGELOG.md`, `RELEASES.md` segundo SemVer adotado

Observação de arquitetura (opcional, fase 2): externalizar categorias para arquivo de configuração (ex.: JSON/YAML) carregado pelo `CategoryDetector` mantendo fallback interno.

## 📋 Tarefas
- [x] Expandir dicionário de categorias e sinônimos em `src/category_detector.py`
- [x] Implementar alias mapping para categorias similares
- [ ] Context-based detection: incorporar boosts por título/subtítulo/URL
- [ ] Integrar contexto em `sources/tomada_tempo.py` → `CategoryDetector`
- [ ] Garantir que `src/ical_generator.py` reflita categorias corretas
- [ ] Testes unitários de parsing/detecção
- [ ] Testes de integração da fonte Tomada de Tempo
- [ ] Atualizar documentação (README, DATA_SOURCES, CHANGELOG, RELEASES)

## 🔧 Atualizações recentes
- Correção: semântica do campo `source` em `CategoryDetector.detect_categories_batch`.
  - Quando `raw_category` estiver presente (match exato, sem contexto) → `source = "pattern_matching"`.
  - Quando precisar combinar com contexto (`name`/outros) → `source = "pattern_matching+context"`.
- Teste ajustado: `tests/unit/category/test_category_detector_filter_and_batch.py::test_detect_categories_batch_combines_name_and_handles_empty`.
- Sem mudanças de dependências ou configurações.

## 🧪 Plano de Testes
- Unit (pytest): foco em parsing/normalização/matching e alias map
- Integração: fixtures de páginas do Tomada de Tempo cobrindo internacionais/nacionais/regionais
- Erros comuns: títulos ambíguos, HTML parcial, ausência de campo explícito de categoria
- Execução:
  - `pytest -q`
  - `pytest --cov=src --cov-report=term-missing`

## ✅ Critérios de Aceitação
- [ ] ≥95% de cobertura das categorias mencionadas no Tomada de Tempo
- [ ] ≥90% de acurácia na classificação automática (validada em testes)
- [ ] Documentação atualizada

## 📊 Impacto
Médio — melhora a qualidade de classificação e a experiência do usuário, além de facilitar filtros/pesquisas.

## 🔗 Links Relacionados
- Issue: https://github.com/dmirrha/motorsport-calendar/issues/2
- Branch de trabalho: `issue/2-category-detection`

## 📱 Ambiente
- macOS, Python 3.11, pytest/coverage/mutmut, GitHub Actions

## Observações
- Risco monitorado: iCal exibindo categoria incorreta; validar com testes e inspeção do gerador.
