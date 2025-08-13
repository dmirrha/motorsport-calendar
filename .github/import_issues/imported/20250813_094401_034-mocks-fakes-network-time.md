# Fase 2 — Mocks/Fakes de Coleta e Controle de Tempo
Vinculado ao épico: #78

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

## Referências
- `.windsurf/rules/tester.md`
