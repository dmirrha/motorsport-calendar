#!/usr/bin/env bash
set -euo pipefail

# Script: create_patch_0_5_2_pr.sh
# Objetivo: Commit, push e abrir PR (patch 0.5.2) com correções de testes e notas de versão.
# Uso:
#   ./scripts/create_patch_0_5_2_pr.sh            # executa
#   DRY_RUN=1 ./scripts/create_patch_0_5_2_pr.sh  # apenas exibe comandos

BRANCH="chore/tests-path-fix-20250809"
TITLE="chore(tests): patch 0.5.2 — conftest import fix + deterministic weekend test"
LABELS=(maintenance tests semver:patch)

# Corpo da PR (heredoc literal, sem interpolação)
BODY="$(cat <<'PR_BODY'
Progresso do Plano — Fase 0

- [x] Corrigir path dos testes: `tests/conftest.py`
- [x] Tornar teste determinístico: `tests/test_tomada_tempo.py`
- [x] Validar suíte: `37 passed`
- [x] Atualizar documentações: `CHANGELOG.md` (0.5.2), `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`

Escopo
- Sem mudanças funcionais no core; apenas testes e versionamento.

SemVer
- Patch 0.5.2
PR_BODY
)"

# Arquivos esperados nesta mudança
FILES=(
  "CHANGELOG.md"
  "RELEASES.md"
  "docs/TEST_AUTOMATION_PLAN.md"
  "src/__init__.py"
  "tests/test_tomada_tempo.py"
  "tests/conftest.py"
)

# Funções auxiliares ---------------------------------------------------------
run() {
  if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo "[DRY_RUN] $*"
  else
    echo "> $*"
    eval "$*"
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Erro: comando '$1' não encontrado." >&2; exit 1; }
}

# Pré-checagens --------------------------------------------------------------
require_cmd git
require_cmd gh

# Verifica se label existe no repositório
has_label() {
  gh label list --search "$1" --json name -q '.[].name' | grep -Fxq "$1"
}

# Confirma branch atual
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "$BRANCH" ]]; then
  echo "Erro: branch atual é '$current_branch', esperado '$BRANCH'." >&2
  echo "Troque para a branch correta antes de rodar: git checkout $BRANCH" >&2
  exit 1
fi

# Stage dos arquivos (somente os existentes)
for f in "${FILES[@]}"; do
  if [[ -e "$f" ]]; then
    run "git add '$f'"
  else
    echo "Aviso: arquivo não encontrado e será ignorado: $f"
  fi
done

# Commit (se houver mudanças)
if ! git diff --cached --quiet; then
  run "git commit -m 'chore(tests): fix imports via tests/conftest.py and make weekend filter test deterministic; bump version to 0.5.2 (SemVer patch)' -m '- 37 tests passing
- Update CHANGELOG.md and RELEASES.md
- Update docs/TEST_AUTOMATION_PLAN.md'"
else
  echo "Nada para commitar (índice sem mudanças). Prosseguindo."
fi

# Push com upstream
run "git push -u origin $BRANCH"

# Se já existir PR para a head branch, apenas exibe a URL
if gh pr view --head "$BRANCH" >/dev/null 2>&1; then
  url=$(gh pr view --head "$BRANCH" --json url -q .url)
  echo "PR já existe: $url"
  exit 0
fi

# Monta labels existentes
label_args=()
for l in "${LABELS[@]}"; do
  if has_label "$l"; then
    label_args+=("--label" "$l")
  else
    echo "Aviso: label não existe e será ignorada: $l"
  fi
done

# Cria PR usando --body-file para evitar execução de crases/backticks
BODY_FILE=$(mktemp -t pr_body.XXXXXX.md)
printf '%s\n' "$BODY" > "$BODY_FILE"

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  label_flags=""
  if ((${#label_args[@]})); then
    for lf in "${label_args[@]}"; do
      label_flags+=" ${lf}"
    done
  fi
  echo "[DRY_RUN] gh pr create --base main --head '$BRANCH' --title \"$TITLE\" --body-file '$BODY_FILE'${label_flags}"
else
  if ((${#label_args[@]})); then
    if gh pr create --base main --head "$BRANCH" --title "$TITLE" --body-file "$BODY_FILE" "${label_args[@]}"; then
      :
    else
      echo "Falha ao criar PR" >&2
      rm -f "$BODY_FILE"
      exit 1
    fi
  else
    if gh pr create --base main --head "$BRANCH" --title "$TITLE" --body-file "$BODY_FILE"; then
      :
    else
      echo "Falha ao criar PR" >&2
      rm -f "$BODY_FILE"
      exit 1
    fi
  fi
fi

rm -f "$BODY_FILE"

echo "Concluído."
