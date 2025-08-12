.PHONY: help test test.unit test.integration coverage report clean

PYTEST ?= pytest
PYTEST_ARGS ?=

help:
	@echo "Targets:" && \
	echo "  make test            # roda pytest com addopts do pytest.ini (inclui cobertura e gate 45%)" && \
	echo "  make test.unit       # roda apenas testes marcados como unit" && \
	echo "  make test.integration# roda apenas testes marcados como integration" && \
	echo "  make coverage        # executa pytest gerando relatórios de cobertura (html/xml)" && \
	echo "  make report          # mostra onde encontrar os relatórios" && \
	echo "  make clean           # remove artefatos de testes"

# Usa addopts do pytest.ini (inclui cobertura, relatórios e --cov-fail-under=45)
test:
	$(PYTEST) $(PYTEST_ARGS)

# Execução rápida de unit tests
test.unit:
	$(PYTEST) -m unit -q $(PYTEST_ARGS)

# Execução de testes de integração
test.integration:
	$(PYTEST) -m integration $(PYTEST_ARGS)

# Gera relatórios de cobertura (respeita o gate 45% do pytest.ini)
coverage:
	$(PYTEST) $(PYTEST_ARGS)

report:
	@echo "Relatórios de cobertura e testes:" && \
	echo "  HTML coverage: htmlcov/index.html" && \
	echo "  XML coverage:  coverage.xml" && \
	echo "  JUnit XML:     test_results/junit.xml"

clean:
	rm -rf .pytest_cache htmlcov .coverage .coverage.* coverage.xml junit.xml test_results
