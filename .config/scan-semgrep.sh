#!/bin/sh
set -eu

revision=16b9e6d45f10649f6a531ec4838ed9924372c3bc
rules=$(mktemp -d)
trap 'rm -rf "$rules"' EXIT
git -C "$rules" init --quiet
git -C "$rules" fetch --quiet --depth=1 https://github.com/semgrep/semgrep-rules.git "$revision"
git -C "$rules" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$rules" rev-parse HEAD)" = "$revision"

report=$1
profile=$2
shift 2

set -- --config "$rules/yaml/github-actions/security" "$@"
case "$profile" in
typescript)
  set -- --config "$rules/typescript/lang/security" --config "$rules/javascript/lang/security" "$@"
  ;;
python)
  set -- --config "$rules/python/lang/security" --config "$rules/bash/lang/security" --config "$rules/bash/curl/security" "$@"
  ;;
hugo)
  set -- --config "$rules/dockerfile/security" --config "$rules/bash/lang/security" --config "$rules/bash/curl/security" "$@"
  ;;
*)
  exit 2
  ;;
esac

mkdir -p "$(dirname "$report")"
semgrep scan --validate --metrics off "$@"
semgrep scan --error --no-git-ignore --no-rewrite-rule-ids --metrics off --sarif-output "$report" "$@"
