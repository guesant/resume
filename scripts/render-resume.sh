#!/usr/bin/env bash
set -euo pipefail

rendercv_image='ghcr.io/rendercv/rendercv@sha256:699aaee00c9e6754e75bdfbbc37439d6e94ec32d67f0e4065b276ab8b66929f7'
repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$repository_root/build" "$repository_root/site/en" "$repository_root/site/pt-BR"

for locale in en pt-BR; do
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    --env HOME=/tmp \
    --volume "$repository_root:/work" \
    --workdir /work \
    "$rendercv_image" \
    render "cv/${locale}.yaml" --quiet
done

cp "$repository_root/build/en/Gabriel_R._Antunes_CV.pdf" "$repository_root/site/en/resume.pdf"
cp "$repository_root/build/en/Gabriel_R._Antunes_CV.html" "$repository_root/site/en/index.html"
cp "$repository_root/build/pt-BR/Gabriel_R._Antunes_CV.pdf" "$repository_root/site/pt-BR/curriculo.pdf"
cp "$repository_root/build/pt-BR/Gabriel_R._Antunes_CV.html" "$repository_root/site/pt-BR/index.html"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  --volume "$repository_root:/work" \
  --workdir /work \
  --entrypoint python \
  "$rendercv_image" \
  /work/scripts/export-lobby.py

