#!/usr/bin/env bash
set -euo pipefail

mkdir -p .local/reports/sarif
files=(--lockfile .config/python/uv.lock)
reports=()
for lockfile in .config/tooling/*/pnpm-lock.yaml; do
  report=".local/reports/sbom/${lockfile%/pnpm-lock.yaml}/dependencies.cdx.json"
  files+=(--lockfile "$report")
  reports+=("$report")
done

json_status=0
sarif_status=0
osv-scanner scan source --experimental-plugins sbom --all-packages "${files[@]}" --format json >.local/reports/osv.json || json_status=$?
osv-scanner scan source --experimental-plugins sbom --all-packages "${files[@]}" --format sarif >.local/reports/sarif/osv.sarif || sarif_status=$?
if ((json_status > 1 || json_status != sarif_status)); then
  exit 2
fi

python3 .config/check-osv.py .local/reports/osv.json "${reports[@]}"
