#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rendercv_image='ghcr.io/rendercv/rendercv@sha256:699aaee00c9e6754e75bdfbbc37439d6e94ec32d67f0e4065b276ab8b66929f7'

docker run --rm \
  --volume "$repository_root:/work" \
  --workdir /work \
  --entrypoint python \
  "$rendercv_image" \
  /work/scripts/validate-videos.py

test -s "$repository_root/site/en/index.html"
test -s "$repository_root/site/en/resume.pdf"
test -s "$repository_root/site/pt-BR/index.html"
test -s "$repository_root/site/pt-BR/curriculo.pdf"

for file in "$repository_root/site/en/index.html" "$repository_root/site/pt-BR/index.html"; do
  ! grep -Fq 'John Doe' "$file"
  ! grep -Fq 'TODO' "$file"
done

