#!/usr/bin/env bash
set -euo pipefail

mkdir -p .local/reports/sarif
status=0
trivy image --input .local/scan-image.tar --no-progress --scanners vuln \
  --severity HIGH,CRITICAL --exit-code 1 --format sarif \
  --output .local/reports/sarif/trivy-image.sarif || status=$?
trivy image --input .local/scan-image.tar --no-progress --format cyclonedx \
  --output .local/reports/sbom.cdx.json
exit "$status"
