#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
OUT_DIR="test_results/inventory"
TS="$(date +%Y%m%d-%H%M%S)"
OUT_FILE="$OUT_DIR/phase0_inventory_${TS}.md"

mkdir -p "$OUT_DIR"

{
  echo "# Inventário Fase 0 — $(date -Iseconds)"
  echo
  echo "- CWD: $ROOT"
  echo "- Branch: $(git branch --show-current 2>/dev/null || echo 'n/a')"
  echo

  echo "## 1) Testes fora de \`tests/\`"
  echo "### Arquivos fora de tests/ (test_*.py)"
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './.pytest_cache' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type f -name 'test_*.py' -not -path './tests/*' -print || true
  echo
  echo "### Arquivos fora de tests/ (*_test.py)"
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './.pytest_cache' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type f -name '*_test.py' -not -path './tests/*' -print || true
  echo
  echo "### Diretórios \`tests\` fora da raiz \`./tests\`"
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './.pytest_cache' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type d -name 'tests' ! -path './tests' -print || true
  echo

  echo "## 2) Artefatos gerados versionados"
  echo "### Diretórios"
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type d -name '.pytest_cache' -print || true
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type d -name 'htmlcov' -print || true
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type d -name 'test_results' -print || true
  echo
  echo "### Arquivos"
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type f -name '.coverage*' -print || true
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type f -name 'coverage.xml' -print || true
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './venv' -prune -o \
    -path './env' -prune -o \
    -path './.tox' -prune -o \
    -path './node_modules' -prune -o \
    -path './build' -prune -o \
    -path './dist' -prune -o \
    -type f -name 'junit.xml' -print || true
  echo

  echo "## 3) Scripts temporários de testes (scripts/)"
  if [ -d scripts ]; then
    ls -la scripts/ | grep -E 'tmp_.*(tester|tests).*\.sh' || true
  else
    echo 'scripts/ (não existe)'
  fi
  echo

  echo "## 4) Workflows de CI (.github/workflows/)"
  if [ -d .github/workflows ]; then
    ls -la .github/workflows/ || true
  else
    echo '.github/workflows/ (não existe)'
  fi
  echo

  echo "## 5) Configurações antigas de teste (nose/tox)"
  find . -maxdepth 3 -type f \( -name 'nose.cfg' -o -name 'tox.ini' \) -print || true
  echo
} > "$OUT_FILE"

# Reportar o caminho do relatório gerado
echo "Relatório salvo em: $OUT_FILE"
echo "$OUT_FILE"
