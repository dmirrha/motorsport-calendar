# Plano de Automação de Testes — Race Calendar

## Objetivo
Estabelecer uma estratégia simples e efetiva para implementar e evoluir testes automatizados, com execução local e no GitHub Actions, incluindo relatórios de cobertura e de execução.

## Escopo e Princípios
- Foco no essencial: parsers, validadores e processadores de dados.
- Pytest como framework principal. Unittest apenas quando necessário.
- Mocks simples para I/O e rede (requests/Session).
- Cobertura pragmática via pytest-cov; metas progressivas.
- Execução local idêntica ao CI (paridade de comandos).

## Tecnologias
- pytest, pytest-cov, pytest-xdist (paralelo opcional)
- unittest.mock (mocks/patches)
- requests, BeautifulSoup (scraping estático)
- actions/setup-python (CI), upload-artifact (artefatos)

## Estrutura do Projeto (relevante a testes)
- Código: `src/motorsport_calendar/` e `sources/`
- Testes: `tests/` (existente, amplo)
- Artefatos: `test_results/`, `junit.xml`, `htmlcov/` (gerados)
- CI: `.github/workflows/` (atualmente sem workflow de testes)

## Diretrizes de Documentação e Rastreamento
Objetivo: Garantir documentação padrão, simples e completa para explicar a estratégia de testes e permitir rastreabilidade fina das atividades, conforme `.windsurf/rules/tester.md` e políticas do projeto.

## Checklist — Documentação Padrão
- [ ] Criar/atualizar visão geral de testes em `docs/tests/overview.md` (estratégia, escopo, como rodar local/CI, estrutura de pastas)
- [ ] Criar índice de cenários em `docs/tests/scenarios/SCENARIOS_INDEX.md` (links para cenários por fase)
- [ ] Criar/atualizar mapeamento de cenários por fase:
  - [ ] `docs/tests/scenarios/phase0_scenarios.md` (inventário e decisões de limpeza)
  - [ ] `docs/tests/scenarios/phase1_scenarios.md` (parsers/validação/utils)
  - [ ] `docs/tests/scenarios/phase2_scenarios.md` (fluxos de integração e iCal)
- [ ] Atualizar documentações obrigatórias a cada mudança testada:
  - [ ] `CHANGELOG.md`, `CONTRIBUTING.md`, `DATA_SOURCES.md`, `PROJECT_STRUCTURE.md`, `README.md`, `RELEASES.md`, `REQUIREMENTS.md`, `CONFIGURATION_GUIDE.md`, `docs/TEST_AUTOMATION_PLAN.md`
- [ ] Processo de tracking
  - [ ] Toda descoberta/melhoria gera itens no plano em formato checklist, e issues quando aplicável (via GH)
  - [ ] Registrar no(s) arquivo(s) de cenários o status (ToDo/Doing/Done) e referência a PRs/Issues

# Fase 0 — Limpeza do Repositório
Objetivo: Remover legados e padronizar a base de testes antes de iniciar as fases seguintes, seguindo a simplicidade descrita em `.windsurf/rules/tester.md`.

## Checklist — Fase 0 (ordem sequencial)
- [ ] Inventário de pastas/arquivos de teste
  - [ ] Mapear tudo fora de `tests/` (padrões: `test_*.py`, `*_test.py`, `tests*/`, `.pytest_cache`, `htmlcov`, `junit.xml`, `coverage.xml`, `.coverage*`)
  - [ ] Identificar scripts temporários em `scripts/` (ex.: `tmp_*tester*.sh`, `tmp_*tests*.sh`)
- [ ] Definir padrão canônico
  - [ ] Manter apenas `tests/` como pasta oficial de testes
  - [ ] Mover para `tests/` arquivos válidos encontrados fora do padrão; excluir duplicatas
- [ ] Backup antes de remover
  - [ ] Criar branch `chore/tests-cleanup-YYYYMMDD` e tag `backup/tests-cleanup-YYYYMMDD`
  - [ ] Opcional: arquivar em `docs/archive/tests/YYYYMMDD/` itens potencialmente úteis
- [ ] Remover frameworks/arquivos obsoletos
  - [ ] Excluir `nose.cfg`, `tox.ini` e configs antigas não utilizadas
  - [ ] Unificar configuração em único `pytest.ini` (sem `setup.cfg`/`pyproject.toml` para testes)
- [ ] Normalização de nomes/estrutura
  - [ ] Garantir padrão de arquivo `test_*.py`
  - [ ] Remover `__init__.py` em `tests/` (a menos que necessário)
- [ ] Limpeza de artefatos gerados
  - [ ] Excluir `.pytest_cache/`, `htmlcov/`, `.coverage*`, `coverage.xml`, `junit.xml`, `test_results/`
  - [ ] Atualizar `.gitignore` para garantir ignorados consistentes
- [ ] Scripts temporários e dispersos
  - [ ] Revisar `scripts/` e remover scripts temporários relacionados a testes que não serão usados
- [ ] CI antigo
  - [ ] Remover workflows antigos/duplicados de testes; manter apenas `tests.yml` quando criado
- [ ] Validação pós-limpeza
  - [ ] Executar `pytest -q` para confirmar descoberta apenas em `tests/`
  - [ ] Documentar no `CHANGELOG.md` e atualizar `README.md`/`REQUIREMENTS.md` se aplicável
- [ ] Documentação e rastreabilidade (Fase 0)
  - [ ] Criar/atualizar `docs/tests/scenarios/phase0_scenarios.md` com inventário, decisões e itens derivados
  - [ ] Adicionar itens derivados como checklist nesta seção do plano (`docs/TEST_AUTOMATION_PLAN.md`)

# Fase 1 — Testes Unitários
Objetivo: Cobrir funções críticas de parsing/transformação/validação com testes rápidos, determinísticos e independentes de rede/FS.

## Checklist — Fase 1 (ordem sequencial)
- [ ] Configuração mínima do Pytest
  - [ ] Criar `pytest.ini`
    - [ ] Descoberta em `tests/`
    - [ ] Cobertura de `src/` e `sources/`
    - [ ] Relatórios: term-missing, XML (coverage.xml), HTML (htmlcov), JUnit (test_results/junit.xml)
    - [ ] Fail gate inicial (ex.: `--cov-fail-under=70`), com roadmap para 80%
- [ ] Organização de testes
  - [ ] Introduzir marcadores `@pytest.mark.unit`
  - [ ] Criar/ajustar `conftest.py` com fixtures reutilizáveis (HTML mínimo, fuso horário padrão, relógio congelado)
- [ ] Mocks essenciais
  - [ ] Definir padrões de patch (compatíveis com shims):
    - [ ] `sources.tomada_tempo.requests.get`
    - [ ] `sources.base_source.requests.Session`
  - [ ] Simular cenários: sucesso, timeout, HTTPError, HTML malformado
- [ ] Alvos prioritários (unit)
  - [ ] Parsers de data/hora e categorias em `sources/tomada_tempo.py`
  - [ ] Normalização/validação no `src/motorsport_calendar/event_processor.py`
  - [ ] Utilitário iCal `src/motorsport_calendar/utils/ical_generator.py` (`generate_ical`)
- [ ] Geração de cenários (unit)
  - [ ] Criar diretório `tests/fixtures/` (se necessário)
  - [ ] HTMLs mínimos para parsing (datas/horas, categorias, campos faltantes)
  - [ ] Matrizes de casos para horários: 24h, AM/PM, sem minutos, overnight, naive vs aware
  - [ ] Cenários de categoria: conhecidas vs fallback `Unknown`
  - [ ] Casos iCal: PRODID, DTSTART/DTEND com TZ, URL, CATEGORIES, RRULE com `recurrence`
- [ ] Documentação e rastreabilidade (Fase 1)
  - [ ] Criar/atualizar `docs/tests/scenarios/phase1_scenarios.md` (matriz de casos, mapeamentos, status e links para testes)
  - [ ] Adicionar itens derivados como checklist nesta seção do plano

6) Execução e relatórios (local)
- Instalação: `pip install -r requirements.txt && pip install pytest pytest-cov`
- Execução rápida (unit):
  - `pytest -m unit --cov=src --cov=sources --cov-report=term-missing:skip-covered \
     --cov-report=xml:coverage.xml --cov-report=html -q --junitxml=test_results/junit.xml`

7) Critérios de aceite (Fase 1)
- Cobertura global ≥ 70% (meta subir para 80%).
- Testes determinísticos (< 30s localmente em máquina média).
- Relatórios HTML/ XML gerados e versionados apenas como artefatos (não no repo).

---

# Fase 2 — Testes Integrados
Objetivo: Validar fluxos entre componentes (coleta → processamento → iCal), sem dependência externa real (rede) sempre que possível.

## Checklist — Fase 2 (ordem sequencial)
- [ ] Definir escopo de integração
  - [ ] Fluxo mínimo: coleta (mock/fake) → `EventProcessor` → `ICalGenerator`/`utils.generate_ical` → validação do `.ics`
  - [ ] Reaproveitar fixtures e dados de exemplo (HTML mínimo e JSONs de eventos sintéticos)
- [ ] Marcação e seleção
  - [ ] Marcar testes com `@pytest.mark.integration`
  - [ ] Habilitar execução seletiva: `pytest -m integration`
- [ ] Mocks/fakes de borda
  - [ ] Simular finais de semana-alvo e TZ de configuração
  - [ ] Simular eventos sem data explícita (contexto de programação) e overnight
  - [ ] Requisições: respostas estáticas com HTML realista mínimo
- [ ] Geração de cenários (integração)
  - [ ] Fixtures com programação de fim de semana (HTML/JSON) cobrindo múltiplas sessões
  - [ ] Eventos que cruzam meia-noite e múltiplos fusos
  - [ ] Casos com e sem `url`, `category`, `recurrence`
  - [ ] Conjuntos para validar deduplicação, ordenação e consistência de TZ
- [ ] Validações principais
  - [ ] Contagem de eventos processados
  - [ ] VEVENT: SUMMARY, DTSTART/DTEND, UID, URL, CATEGORIES, RRULE (quando aplicável)
  - [ ] Consistência de timezone (naive → localized conforme config)
- [ ] Documentação e rastreabilidade (Fase 2)
  - [ ] Criar/atualizar `docs/tests/scenarios/phase2_scenarios.md` (fluxos, casos, status e links)
  - [ ] Adicionar itens derivados como checklist nesta seção do plano

5) Execução e relatórios (local)
- `pytest -m integration --cov=src --cov=sources --cov-append \
   --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml \
   --cov-report=html --junitxml=test_results/junit.xml`

6) Critérios de aceite (Fase 2)
- Fluxo end-to-end gerando `.ics` válido.
- Cobertura incremental (meta global ≥ 80% ao final da fase).
- Artefatos (JUnit + HTMLCov) disponíveis localmente e no CI.

---

## Execução Local — Guia Rápido
- Instalação:
```
pip install -r requirements.txt
pip install pytest pytest-cov
```
- Unit:
```
pytest -m unit --cov=src --cov=sources --cov-report=term-missing:skip-covered \
  --cov-report=xml:coverage.xml --cov-report=html \
  --junitxml=test_results/junit.xml
```
- Integração:
```
pytest -m integration --cov=src --cov=sources --cov-append \
  --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml \
  --cov-report=html --junitxml=test_results/junit.xml
```

## GitHub Actions — Workflow Sugerido (`.github/workflows/tests.yml`)
```yaml
name: Tests
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Pytest (unit)
        run: |
          pytest -m unit --cov=src --cov=sources \
            --cov-report=term-missing:skip-covered \
            --cov-report=xml:coverage.xml --cov-report=html \
            --junitxml=test_results/junit.xml
      - name: Pytest (integration)
        run: |
          pytest -m integration --cov=src --cov=sources --cov-append \
            --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml \
            --cov-report=html --junitxml=test_results/junit.xml || true
      - name: Upload coverage HTML
        uses: actions/upload-artifact@v4
        with:
          name: htmlcov
          path: htmlcov/
          if-no-files-found: ignore
      - name: Upload JUnit report
        uses: actions/upload-artifact@v4
        with:
          name: junit
          path: test_results/junit.xml
          if-no-files-found: ignore
```
Notas:
- `|| true` no bloco de integração é opcional se a fase 2 ainda não estiver completa; remova quando estabilizar.
- Para gates de cobertura no CI, adicione `--cov-fail-under=<meta>`.

## Convenções e Boas Práticas
- Nomes de testes descritivos: `test_<comportamento>_<cenário>_<resultado>`.
- Um comportamento por teste quando possível.
- Fixtures pequenas e reutilizáveis; evitar hierarquias complexas.
- Mocks só quando necessário para remover efeitos colaterais (rede/FS/tempo).

## Roadmap de Evolução
1. Subir `--cov-fail-under` de 70% → 80% após estabilização da Fase 2.
2. Paralelizar testes com `pytest -n auto` (quando estável e sem condições de corrida).
3. Opcional: adicionar `pytest-rerunfailures` para flakies pontuais.

## Referências
- Guia de simplicidade: `.windsurf/rules/tester.md`.
- Código relevante: `sources/`, `src/motorsport_calendar/`, `tests/`.
- Padrões de patch (shims já mapeados): `sources.tomada_tempo.requests.get`, `sources.base_source.requests.Session`.
