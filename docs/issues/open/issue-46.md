---
issue: 46
title: "Fase 1 — Configuração mínima do Pytest"
epic: 45
milestone: 2
branch: chore/pytest-min-config-46-20250809
created_at: 2025-08-09T20:10:15Z
status: "em andamento (planejamento)"
---

# Issue #46 — Plano de Resolução (Draft)

- Link: https://github.com/dmirrha/motorsport-calendar/issues/46
- Epic: #45
- Milestone: #2 — Automação de testes - Fase 1
- Branch: chore/pytest-min-config-46-20250809

## Descrição
Ver detalhes no JSON: .

## Logs e Evidências
(N/A no início; anexar se surgirem durante a execução)

## Plano de Resolução
- [ ] Definir  base (addopts, testpaths, filtros de warnings)
- [ ] Configurar  (report XML/term, pasta de artefatos)
- [ ] Revisar  (fixtures base e ajuste de )
- [ ] Padronizar TZ  para testes determinísticos
- [ ] Rodar .....................................                                    [100%]
37 passed in 5.30s com coleta apenas em 
- [ ] Definir cobertura mínima inicial (ex.: 40%)
- [ ] Documentar no  e atualizar 
- [ ] Abrir PR mencionando , milestone  e épico 

## Critérios de Aceite
- Execução .....................................                                    [100%]
37 passed in 2.19s determinística localmente
- Cobertura publicada no CI (quando workflow for criado)
- Documentação mínima das opções em /

## PARE
Aguarde aprovação para iniciar as mudanças de configuração (pytest.ini, pytest-cov, conftest, TZ e cobertura mínima).
