#!/usr/bin/env bash
set -euo pipefail

# Limpeza Fase 0 — remover do índice do Git artefatos gerados (mantém arquivos locais)
# Uso:
#   DRY_RUN=1 ./scripts/tests_phase0_cleanup.sh   # padrão (não altera nada, apenas mostra)
#   DRY_RUN=0 ./scripts/tests_phase0_cleanup.sh   # executa remoções do índice
#   CREATE_KEEP=1                                 # cria .gitkeep em pastas de resultados

DRY_RUN=${DRY_RUN:-1}
CREATE_KEEP=${CREATE_KEEP:-1}
DATE_TAG=$(date +%Y%m%d)

say() { printf "[cleanup] %s\n" "$*"; }
run() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "+ $*";
  else
    eval "$*";
  fi
}

# Caminhos a desindexar com segurança (mantidos localmente)
DIRS=(
  ".pytest_cache"
  "tests/test_results"
  "tests/unit/test_results"
  "test_results"
  "test_results_github"
)
FILES=(
  "tests/.coverage"
  "tests/unit/.coverage"
  "coverage.xml"
  "junit.xml"
  "test_results/coverage.xml"
  "tests/test_results/coverage.xml"
  "test_results/junit.xml"
  "tests/test_results/junit.xml"
  "tests/unit/test_results/junit.xml"
  "test_results_github/junit.xml"
)

say "Branch atual: $(git branch --show-current 2>/dev/null || echo n/a)"

# Sugerir criação de branch/tag de backup (não executa automaticamente)
say "Sugestão (manual): git switch -c chore/tests-cleanup-${DATE_TAG} && git tag backup/tests-cleanup-${DATE_TAG}"

# Remover diretórios do índice
for d in "${DIRS[@]}"; do
  if [ -e "$d" ]; then
    run "git rm -r --cached --ignore-unmatch '$d'"
  fi
done

# Remover arquivos do índice
for f in "${FILES[@]}"; do
  if [ -e "$f" ]; then
    run "git rm --cached --ignore-unmatch '$f'"
  fi
done

# Criar .gitkeep opcionalmente
if [ "$CREATE_KEEP" = "1" ]; then
  for keepdir in tests/test_results test_results; do
    if [ -d "$keepdir" ]; then
      run "/usr/bin/env bash -lc 'mkdir -p \"$keepdir\" && touch \"$keepdir/.gitkeep\"'"
    fi
  done
fi

say "Status após limpeza (simulado se DRY_RUN=1):"
run "git status --porcelain"

say "Para confirmar limpeza real, rode: DRY_RUN=0 ./scripts/tests_phase0_cleanup.sh"
say "Commit sugerido: chore(tests): phase0 cleanup — remove artefatos gerados do índice"
say "Atualize CHANGELOG.md e docs conforme sua política SemVer."
