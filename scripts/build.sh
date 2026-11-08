#!/usr/bin/env bash
set -euo pipefail

bash scripts/render-resume.sh
bash scripts/validate-output.sh
