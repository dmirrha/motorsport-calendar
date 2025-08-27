# Issue 159 — F2 (opcional): Regras simples de detecção de anomalias

- Número: 159
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/159
- Criado em: 2025-08-26T16:56:22Z
- Atualizado em: 2025-08-26T17:09:11Z
- Labels: enhancement, needs-triage, ai, optional, priority: P3

## Contexto
Implementar checagens leves de qualidade para sinalizar anomalias (datas fora do fim de semana alvo, horários improváveis, inconsistências de local/categoria), sem bloquear o pipeline. Reportar anomalias agregadas ao final do processamento. Integrar com `src/event_processor.py` (ou módulo auxiliar) e expor o resumo no log/UI.

Referências: `src/event_processor.py`, `docs/architecture/ai_implementation_plan.md`.

## Objetivo
- Gerar um relatório de warnings com contagens e exemplos de anomalias.
- Não alterar o fluxo principal (apenas sinalização/log). Opcional/sem impacto quando desativado.

## Escopo
- Regras e severidades (warning/info) definidas e documentadas.
- Coleta e agregação de casos durante o pipeline.
- Exposição do resumo no logger/UI ao final do `process_events()`.
- Configuração para ativar/desativar e ajustar limites básicos.

## Critérios de Aceitação
- [ ] Regras documentadas e configuráveis quando aplicável.
- [ ] Testes cobrindo casos positivos/negativos (cenários sintéticos).
- [ ] Sem impacto na geração quando desativado.

## Plano de Resolução (proposto)
1) Estrutura de Anomalias
- Criar `AnomalyRule` (protocolo simples) e `AnomalyReport` para agregação.
- Implementar `AnomalyDetector` opcional, acoplado ao `EventProcessor` via config.

2) Regras iniciais (warning)
- Data fora do fim de semana alvo (`target_weekend`).
- Horário improvável (ex.: < 06:00 ou > 23:59 local) — limites configuráveis.
- Inconsistência de categoria (ex.: `raw_category` vazio com `detected_category` baixa confiança).
- Local ausente ou não normalizado (heurísticas simples).

3) Integração no pipeline
- Avaliar após normalização/categorização e antes/depois do filtro de fim de semana conforme a regra.
- Agregar por tipo de anomalia com amostras (até N exemplos por tipo).
- Ao final de `process_events()`, logar um resumo estruturado via logger/UI.

4) Configuração
- Chave `quality.anomaly_detection.enabled` (default: false).
- Limites: `quality.anomaly_detection.hours.min`, `hours.max`, `examples_per_type`, etc.
- Validar via `src/utils/config_validator.py`.

5) Testes e documentação
- Adicionar testes de integração com cenários sintéticos em `tests/integration/`.
- Documentar em `docs/CONFIGURATION_GUIDE.md` e `README.md`.
- Atualizar `CHANGELOG.md` e `RELEASES.md`.

## Checklist de Execução
- [ ] Branch criada: `feat/159-anomaly-rules`.
- [ ] Artefatos locais criados: `docs/issues/open/issue-159.md` e `.json`.
- [ ] Plano confirmado para iniciar implementação.
- [ ] Implementação do `AnomalyDetector` + regras iniciais.
- [ ] Testes e documentação atualizados.

## Logs e Referências
- Arquivos: `src/event_processor.py`, `src/utils/config_validator.py`, `docs/architecture/ai_implementation_plan.md`, `docs/CONFIGURATION_GUIDE.md`, `CHANGELOG.md`, `RELEASES.md`.
- Issue GH: https://github.com/dmirrha/motorsport-calendar/issues/159
- Epic relacionada: #157
