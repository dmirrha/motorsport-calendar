# Issue #79 — Fase 2 — Mocks/Fakes de Coleta e Controle de Tempo

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/79
- Regras: `.windsurf/rules/tester.md`

## Descrição
Fornecer mocks/fakes mínimos para rede, tempo e aleatoriedade para tornar testes determinísticos.

## Tarefas
- [ ] Fake de coleta (substitui requests/HTTP com dados locais)
- [ ] Controle de tempo (ex.: freezegun ou wrapper de tempo existente)
- [ ] Estabilizar aleatoriedade/UID quando aplicável
- [ ] Instruções de uso nas fixtures/utilitários

## Critérios de Aceite
- [ ] Testes não acessam rede/FS externo
- [ ] Execução determinística 3× local
- [ ] Documentação em `tests/README.md`

## Progresso
- [ ] Estrutura de fakes definida
- [ ] Execução estável confirmada 3× (<30s)
- [ ] Documentação sincronizada
