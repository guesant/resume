#!/usr/bin/env bash
set -euo pipefail

for lockfile in .config/tooling/*/pnpm-lock.yaml; do
  directory=${lockfile%/pnpm-lock.yaml}
  report="$PWD/.local/reports/sbom/$directory/dependencies.cdx.json"
  mkdir -p "$(dirname "$report")"
  (cd "$directory" && pnpm sbom --lockfile-only --sbom-format cyclonedx --sbom-spec-version 1.6 --out "$report")
done
