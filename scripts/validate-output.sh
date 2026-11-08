#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository_root"

python scripts/validate-videos.py
python -B scripts/test-export-lobby.py

test -s site/lobby.json
test -s site/en/index.html
test -s site/en/resume.pdf
test -s site/pt-BR/index.html
test -s site/pt-BR/curriculo.pdf

for file in site/en/index.html site/pt-BR/index.html; do
  if grep -Fq -e 'John Doe' -e 'TODO' "$file"; then
    printf 'Placeholder content in %s\n' "$file" >&2
    exit 1
  fi
done
