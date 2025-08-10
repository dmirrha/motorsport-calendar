# Suíte de Testes

Este diretório contém a suíte de testes do projeto. A descoberta de testes é limitada a `tests/` via `pytest.ini` (`testpaths = tests`).

## Convenções

- Nome dos arquivos: `test_*.py`
- Estrutura por domínio/componente em `tests/unit/`:
  - `tests/unit/sources/<source_name>/...`
  - `tests/unit/utils/...`
  - `tests/unit/<feature>/...` (ex.: `silent_period`)
- Não usar `__init__.py` nos diretórios de teste (evita pacotes e conflitos de descoberta do Pytest).
- Fixtures reutilizáveis e configurações comuns em `tests/conftest.py`.
- Timezone fixo para testes: `America/Sao_Paulo` (fixture autouse em `tests/conftest.py`).
- Marcadores registrados em `pytest.ini`:
  - `@pytest.mark.unit`
  - `@pytest.mark.integration`

## Estrutura Atual

- `tests/unit/`
  - `sources/tomada_tempo/test_tomada_tempo.py`
  - `utils/test_config_validator.py`
  - `silent_period/test_silent_period.py`
- `tests/integration/` (reservado para testes de integração)
- `tests/regression/` (artefatos e testes de regressão/manual)

## Execução

- Todos os testes: `pytest`
- Unit tests: `pytest -m unit`
- Cobertura: `pytest --cov` (gate de cobertura inicial `--cov-fail-under=40`)

Relatórios são gerados em:
- JUnit XML: `test_results/junit.xml`
- Cobertura HTML: `htmlcov/`
- Cobertura XML: `coverage.xml`

## Diretrizes

- Centralize helpers/fixtures reutilizáveis em `tests/utils/` e/ou `tests/conftest.py`.
- Evite dependências entre testes. Prefira dados de teste determinísticos.
- Se um teste depender de timezone/date, use a fixture de TZ e datas fixas.
- Testes de integração/regressão não devem afetar a descoberta de unit tests.
