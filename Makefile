.PHONY: help test test.unit test.integration coverage report clean ci.pr-run mutmut.run.unit mutmut.run.integration mutmut.run.all mutmut.results mutmut.show mutmut.clean

PYTEST ?= pytest
PYTEST_ARGS ?=
MUTMUT ?= python3 -m mutmut
MUTMUT_ARGS ?=
# Runner base usado pelo mutmut
# -o addopts=   -> ignora addopts definidos em pytest.ini (evita --cov*, --cov-fail-under, etc.)
# -p no:cov     -> desabilita o plugin pytest-cov caso instalado (mutmut usará coverage diretamente via --use-coverage)
# Respeita addopts extras via PYTEST_ARGS (ex.: -n auto)
MUTMUT_RUNNER_BASE = $(PYTEST) -q -x -o addopts= -p no:cov $(PYTEST_ARGS)
BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
WORKFLOW ?= .github/workflows/tests.yml

help:
	@echo "Targets:" && \
	echo "  make test            # roda pytest com addopts do pytest.ini (inclui cobertura e gate 45%)" && \
	echo "  make test.unit       # roda apenas testes marcados como unit" && \
	echo "  make test.integration# roda apenas testes marcados como integration" && \
	echo "  make coverage        # executa pytest gerando relatórios de cobertura (html/xml)" && \
	echo "  make report          # mostra onde encontrar os relatórios" && \
	echo "  make clean           # remove artefatos de testes" && \
	echo "  make mutmut.run.unit        # mutation testing (mutmut) executando apenas testes marcados como unit" && \
	echo "  make mutmut.run.integration # mutation testing (mutmut) executando apenas testes marcados como integration" && \
	echo "  make mutmut.run.all         # mutation testing (mutmut) executando toda a suíte (cuidado: lento)" && \
	echo "  make mutmut-baseline        # mutation testing (mutmut) focado em módulos críticos (baseline)" && \
	echo "  make mutmut.results         # mostra os mutantes sobreviventes" && \
	echo "  make mutmut.show ID=<id>    # mostra diff de um mutante específico" && \
	echo "  make mutmut.clean           # limpa cache do mutmut (.mutmut-cache)" && \
	echo "  make ci.pr-run BRANCH=<branch> [WORKFLOW=path]  # atualiza a branch com main e dispara o workflow Tests via gh"

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

# ---------------------------
# Mutation testing (mutmut)
# ---------------------------
.PHONY: mutmut-baseline

# Executa mutmut contra caminhos de código fonte, usando somente testes unitários
mutmut.run.unit:
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE) -m unit" --paths-to-mutate src
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE) -m unit" --paths-to-mutate sources

# Executa mutmut usando a suíte de integração (marcador integration)
mutmut.run.integration:
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE) -m integration" --paths-to-mutate src
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE) -m integration" --paths-to-mutate sources

# Executa mutmut com toda a suíte (pode ser bem lento!)
mutmut.run.all:
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE)" --paths-to-mutate src
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE)" --paths-to-mutate sources

# Baseline: foca em módulos críticos, executando a suíte completa de testes como runner
mutmut-baseline:
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE)" --paths-to-mutate src/event_processor.py
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE)" --paths-to-mutate src/ical_generator.py
	$(MUTMUT) run $(MUTMUT_ARGS) --use-coverage --tests-dir=tests --runner="$(MUTMUT_RUNNER_BASE)" --paths-to-mutate sources/base_source.py

# Lista mutantes sobreviventes
mutmut.results:
	$(MUTMUT) results

# Mostra diff detalhado de um mutante específico: make mutmut.show ID=<id>
mutmut.show:
	@if [ -z "$(ID)" ]; then \
		echo "Uso: make mutmut.show ID=<id>"; \
		exit 2; \
	fi
	$(MUTMUT) show $(ID)

# Limpa cache do mutmut
mutmut.clean:
	rm -rf .mutmut-cache

# Atualiza a branch da PR com origin/main e dispara o workflow Tests
# Requisitos: working tree limpo e gh CLI autenticado
ci.pr-run:
	@set -euo pipefail; \
	if ! command -v gh >/dev/null 2>&1; then echo "Erro: gh CLI não encontrado. Instale e autentique com 'gh auth login'."; exit 1; fi; \
	if [ -n "$$({ git status --porcelain || true; } | tr -d '\n')" ]; then echo "Erro: working tree suja. Commite, faça stash ou limpe antes de rodar."; exit 1; fi; \
	orig_branch=$$(git rev-parse --abbrev-ref HEAD); \
	echo "Origem: $$orig_branch"; \
	echo "Atualizando refs..."; \
	git fetch --all --prune; \
	echo "Trocando para a branch $(BRANCH)..."; \
	git checkout $(BRANCH); \
	echo "Atualizando $(BRANCH) com origin/main..."; \
	git fetch origin main $(BRANCH) --prune; \
	git merge --no-edit origin/main || true; \
	echo "Enviando push de $(BRANCH)..."; \
	git push -u origin $(BRANCH); \
	repo=$$(gh repo view --json nameWithOwner -q .nameWithOwner); \
	echo "Disparando workflow $(WORKFLOW) em $$repo@$(BRANCH)..."; \
	gh workflow run $(WORKFLOW) -R "$$repo" -r $(BRANCH); \
	sleep 5; \
	run_id=$$(gh run list -R "$$repo" --branch $(BRANCH) -L 1 --json databaseId -q '.[0].databaseId'); \
	echo "RUN_ID=$$run_id"; \
	gh run watch -R "$$repo" $$run_id --exit-status || true; \
	echo; echo "Resumo do run:"; \
	GH_PAGER=cat gh run view -R "$$repo" $$run_id -v || true; \
	echo "Voltando para $$orig_branch..."; \
	git checkout "$$orig_branch"
