#!/usr/bin/env bash
# Local, read-only context. Never print arbitrary branch text into agent context.
set -euo pipefail
command -v jq >/dev/null 2>&1 || exit 0
root="$(jq -er '.cwd | select(type == "string" and length > 0)' 2>/dev/null)" || exit 0
branch="$(git -C "$root" branch --show-current 2>/dev/null)" || exit 0
ticket="$(printf '%s\n' "$branch" | LC_ALL=C grep -Eio '(^|/)[a-z]+-[0-9]+($|[-/])' | head -n 1 | LC_ALL=C grep -Eio '[a-z]+-[0-9]+' | tr '[:lower:]' '[:upper:]')" || exit 0
[ -n "$ticket" ] || exit 0
printf 'AgentTask branch hint: %s. Resolve it with fetch before writing; an explicit user-selected ticket takes precedence.\n' "$ticket"
