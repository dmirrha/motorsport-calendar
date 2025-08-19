.PHONY: help test test.unit test.integration coverage report clean ci.pr-run

PYTEST ?= pytest
PYTEST_ARGS ?=
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
