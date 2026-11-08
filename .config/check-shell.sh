#!/usr/bin/env bash
set -euo pipefail

case "${1:-check}" in
check)
  git -c safe.directory="$PWD" ls-files --cached --others --exclude-standard -z -- '*.sh' | xargs -0 -r shellcheck
  git -c safe.directory="$PWD" ls-files --cached --others --exclude-standard -z -- '*.sh' | xargs -0 -r shfmt -i 2 -d
  ;;
format)
  git -c safe.directory="$PWD" ls-files --cached --others --exclude-standard -z -- '*.sh' | xargs -0 -r shfmt -i 2 -w
  ;;
*)
  exit 2
  ;;
esac
