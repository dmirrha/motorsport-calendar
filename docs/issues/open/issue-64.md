# Issue #64 — Fase 1.1: Documentação e Cenários (sincronismo)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/64
 - PR (draft): https://github.com/dmirrha/motorsport-calendar/pull/73

## Objetivo
Elevar a qualidade da suíte de testes, priorizando confiabilidade sobre números. Foco em parsers, validadores e processadores de dados, garantindo:
- Determinismo (<30s local) e isolamento de rede/FS/TZ/random com mocks simples
- Cobertura de cenários críticos de erro (timeout, 404, HTML malformado, dados faltantes)
- Oráculos claros e asserts diretos
- Documentação e rastreabilidade sincronizadas a cada incremento

Meta de cobertura derivada (não-fim): atingir ≥ 80% quando a qualidade estiver comprovada.

## Plano de Qualidade
1. Análise de risco e foco
   - `sources/tomada_tempo.py`: variações de HTML e datas
   - `src/category_detector.py`: normalização/ambiguidade de categorias
   - `src/config_manager.py`: overrides por env, chaves faltantes, tipos inválidos
   - `src/utils/payload_manager.py`: payloads incompletos/tipos errados
   - `src/ical_generator.py`: campos ICS obrigatórios/TimeZone ausente
2. Cenários críticos a testar
   - Happy path mínimo por módulo e erros comuns (404/timeout/HTML malformado/dados faltantes)
3. Oráculos e verificação
   - Asserts diretos; validações de estrutura/valores; uso de fixtures simples
4. Determinismo e isolamento
   - Sem IO/rede reais; mocks de requests/FS; fixar TZ e random quando aplicável
5. Entregas iterativas
   - Após cada incremento: atualizar `docs/tests/scenarios/*.md`, `docs/TEST_AUTOMATION_PLAN.md`, `CHANGELOG.md`, `RELEASES.md`
6. Gate de cobertura
   - Manter o gate atual até estabilizar a qualidade; elevar somente após suíte estável e rápida

## PARE — Autorização
- PR inicia em draft até validação deste plano.
 
## Critérios de Aceite
- Suíte determinística (<30s local)
- Cenários críticos cobertos nos módulos foco (incluindo erros comuns)
- Zero flakes em 3 execuções locais consecutivas
- Documentação e rastreabilidade sincronizadas a cada incremento
- Cobertura global resultante ≥ 70% antes de elevar gate; objetivo final ≥ 80% quando a qualidade estiver comprovada

## Progresso
- [x] Branch criada
- [x] PR (draft) aberta — PR #73: https://github.com/dmirrha/motorsport-calendar/pull/73
- [x] Documentação atualizada
 - [x] Releases/Changelog atualizados

### Incremento atual: PayloadManager e ICalGenerator

- Novos testes:
  - `tests/unit/utils/test_payload_manager_errors.py`
  - `tests/unit/ical/test_ical_generator_branches.py`
- Ajustes de testes:
  - Construtor de `ICalGenerator`: uso correto do parâmetro `config_manager` no teste
  - `PayloadManager.save_payload`: exceção encapsulada validada como `IOError`
- Métricas (pós-incremento):
  - Suíte: **205 passed**; cobertura global: **61.52%**
  - `src/utils/payload_manager.py`: **90%**
  - `src/ical_generator.py`: **93%**
- Próximos passos:
  - Executar suíte 3× localmente para confirmar zero flakes
  - Sincronizar documentação correlata (`README.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`)
  - Manter PR #73 como draft na branch `chore/issue-64-coverage-80`

 - [ ] Cobertura unitária ≥ 80% (meta)
