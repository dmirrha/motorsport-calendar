#!/usr/bin/env bash
set -euo pipefail

# Movimentação Fase 0 — mover arquivos de teste fora de ./tests para ./tests
# Uso:
#   DRY_RUN=1 ./scripts/tests_phase0_move_outside_tests.sh   # padrão (não move, apenas mostra)
#   DRY_RUN=0 ./scripts/tests_phase0_move_outside_tests.sh   # aplica as movimentações

DRY_RUN=${DRY_RUN:-1}

say() { printf "[move-tests] %s\n" "$*"; }
run() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "+ $*";
  else
    eval "$*";
  fi
}

# Garantir pasta de destino
if [ ! -d tests ]; then
  run "mkdir -p tests"
fi

# Encontrar candidatos fora de ./tests (compatível com bash 3.2)
tmp_list=$(mktemp -t move_tests_list.XXXXXX)
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
  -path './tests' -prune -o \
  -type f \( -name 'test_*.py' -o -name '*_test.py' \) -print > "$tmp_list" || true

if [ ! -s "$tmp_list" ]; then
  say "Nenhum arquivo de teste fora de ./tests encontrado."
  rm -f "$tmp_list"
  exit 0
fi

say "Arquivos a avaliar para movimentação:"
while IFS= read -r src; do
  echo " - $src"
done < "$tmp_list"

# Planejar e mover
while IFS= read -r src; do
  base="$(basename "$src")"
  dir="$(dirname "$src")"
  target_name="$base"

  # Normalizar nome: *_test.py -> test_*.py
  if [[ "$base" == *_test.py ]]; then
    stem="${base%_test.py}"
    target_name="test_${stem}.py"
  fi

  dest="tests/${target_name}"

  if [ -e "$dest" ]; then
    say "AVISO: destino já existe, pulando: $dest (origem: $src)"
    continue
  fi

  say "Mover: $src -> $dest"
  run "git mv '$src' '$dest' || mv '$src' '$dest'"

done < "$tmp_list"

rm -f "$tmp_list"

say "Concluído. Revise com: git status"
