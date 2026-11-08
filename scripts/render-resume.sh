#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository_root"

mkdir -p build site/en site/pt-BR
python scripts/technologies.py

for locale in en pt-BR; do
  rendercv render "build/inputs/${locale}.yaml" --quiet
done

cp build/en/Gabriel_R._Antunes_CV.pdf site/en/resume.pdf
cp build/en/Gabriel_R._Antunes_CV.html site/en/index.html
cp build/pt-BR/Gabriel_R._Antunes_CV.pdf site/pt-BR/curriculo.pdf
cp build/pt-BR/Gabriel_R._Antunes_CV.html site/pt-BR/index.html

python scripts/export-lobby.py
