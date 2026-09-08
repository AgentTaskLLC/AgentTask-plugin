#!/usr/bin/env bash
# Optional Claude status line; no network access or workspace writes.
set -euo pipefail
command -v jq >/dev/null 2>&1 || exit 0
root="$(jq -er '(.workspace.current_dir | select(type == "string" and length > 0)) // (.cwd | select(type == "string" and length > 0))' 2>/dev/null)" || exit 0
[ -d "$root" ] || exit 0
if repo_root="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null)"; then
  root="$repo_root"
fi
total=0
standing=0
for file in "$root"/.claude/agents/*.md; do
  if [ ! -f "$file" ] || [ -L "$file" ]; then
    continue
  fi
  grep -Eq '^<!-- agent-task crew: [0-9a-fA-F-]{36}( |$)' "$file" || continue
  total=$((total + 1))
  if grep -Eq '^<!-- agent-task cadence: (loop|daily) -->$' "$file"; then
    standing=$((standing + 1))
  fi
done
[ "$total" -gt 0 ] || exit 0
if [ "$standing" -gt 0 ]; then
  printf 'crews: %d (%d standing)\n' "$total" "$standing"
else
  printf 'crews: %d\n' "$total"
fi
