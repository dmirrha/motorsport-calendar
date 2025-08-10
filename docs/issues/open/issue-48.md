# Issue #48 — Fase 1: Mocks essenciais

Referências:
- Epic: #45 — Automação de testes
- Milestone: #2 — Automação de testes - Fase 1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/48

## Objetivo
Garantir determinismo e isolamento em testes unitários por meio de mocks básicos de tempo, aleatoriedade, rede, sistema de arquivos e variáveis de ambiente.

## Plano de Execução
1. Mock de tempo TZ-aware e aleatoriedade
   - Fixture para data/hora fixa (TZ `America/Sao_Paulo`) via `monkeypatch` de `datetime`/`time`
   - Fixture para `random.seed(0)` com restauração
2. Mock de rede
   - Evitar chamadas externas em unit tests
   - Usar `monkeypatch`/stubs em `requests.get`/`requests.post`
3. Isolamento de filesystem
   - Utilizar `tmp_path`/`tmp_path_factory` para arquivos temporários
   - Redirecionar quaisquer paths de escrita/leitura nos testes
4. Variáveis de ambiente
   - Fixture para `monkeypatch.setenv`/`delenv`
5. Documentação e exemplos
   - Atualizar `tests/README.md` com convenções de mocks
   - Adicionar exemplos mínimos em testes existentes
6. Validação
   - Executar `pytest --maxfail=1 -q` e garantir resultados estáveis

## PARE — Autorização
- Submeter PR de rascunho do plano para aprovação antes de alterar testes existentes.

## Progresso
- [x] Branch criada: `chore/tests-mocks-essenciais-48-20250810`
- [x] PR de rascunho aberto com este plano (referenciando #48 e épico #45)
- [ ] Fixtures de tempo e random criadas
- [ ] Mocks de rede definidos
- [ ] Isolamento de FS aplicado com `tmp_path`
- [ ] Fixtures de env aplicadas
- [ ] `tests/README.md` atualizado (seção de mocks)
- [ ] Validação: `pytest` estável sem dependências externas

## Critérios de Aceite
- Testes não dependem de rede/tempo/FS real
- Execução repetível e estável
- Convenções documentadas em `tests/README.md`
