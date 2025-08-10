# Issue #60 — Fase 1.1: Cobertura de sources/base_source.py ≥60% (erros/retries)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/60

## Objetivo
Elevar cobertura de `sources/base_source.py` para ≥60%, cobrindo tratamento de erros e políticas de retry.

## Plano de Execução
1. Testar timeouts, HTTP errors (4xx/5xx), backoff/retries e limites
2. Mockar `requests` e simular exceções
3. Cobrir logging e caminhos de falha (retornos nulos, validação de payload)
4. Atualizar documentação e rastreabilidade (planos, cenários, tests/README, CHANGELOG)

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [x] Branch criada
- [ ] PR (draft) aberta
- [ ] Testes implementados e passando
- [ ] Documentação sincronizada
