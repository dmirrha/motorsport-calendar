# F2 (opcional): Regras simples de detecção de anomalias

## 📝 Descrição
Implementar checagens leves de qualidade para sinalizar anomalias (datas fora do fim de semana alvo, horários improváveis, inconsistências de local/categoria), sem bloquear o pipeline.

## 🔍 Contexto
- Reportar anomalias agregadas ao final do processamento.
- Integrar com `EventProcessor` ou módulo auxiliar.

## 🎯 Comportamento Esperado
- Geração de um relatório de warnings com contagens e exemplos.
- Sem alterar o fluxo principal (apenas sinalização/log).

## 🛠️ Passos
1. Definir regras e severidades (warning/info).
2. Implementar coleta e agregação dos casos.
3. Expor resumo no log/UI.
4. Testes com cenários sintéticos.

## 📋 Critérios de Aceitação
- [ ] Regras documentadas e configuráveis se aplicável.
- [ ] Testes cobrindo casos positivos/negativos.
- [ ] Sem impacto na geração quando desativado.

## 📊 Impacto
Baixo/Médio — melhora a confiabilidade percebida.

## 🔗 Relacionamento
- EPIC: #157

## 🔗 Referências
- `src/event_processor.py`
- `docs/architecture/ai_implementation_plan.md`
