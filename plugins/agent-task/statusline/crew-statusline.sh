#!/usr/bin/env bash
# Agent Task — status line showing active/standing crews (AI-1209).
#
# Wire it into Claude Code via settings.json:
#   { "statusLine": { "type": "command",
#       "command": "bash \"${CLAUDE_PLUGIN_ROOT}/statusline/crew-statusline.sh\"" } }
#
# Claude Code pipes a JSON status payload on stdin (cwd, model, …). We ignore it and scan the
# repo's `.claude/agents/` for crew files stamped by `/crews sync` (the stamp line carries the
# crew uuid). Standing crews are those whose synced file records a non-on_demand cadence.
#
# Output is a single compact line, e.g.:  🤖 crews: 3 (2 standing)
set -euo pipefail

# Drain stdin (Claude Code sends a JSON blob); we don't need it.
cat >/dev/null 2>&1 || true

AGENTS_DIR=".claude/agents"
[ -d "$AGENTS_DIR" ] || exit 0   # nothing to show → empty status line

total=0
standing=0
for f in "$AGENTS_DIR"/*.md; do
  [ -e "$f" ] || continue
  # Only count files stamped by Agent Task /crews sync.
  grep -qi "from Agent Task (synced" "$f" || continue
  total=$((total + 1))
  # A standing crew's synced file mentions a cadence (loop/daily) or a /loop wiring.
  if grep -qiE "cadence:[[:space:]]*(loop|daily)|/loop|standing crew" "$f"; then
    standing=$((standing + 1))
  fi
done

[ "$total" -eq 0 ] && exit 0

if [ "$standing" -gt 0 ]; then
  printf '🤖 crews: %d (%d standing)\n' "$total" "$standing"
else
  printf '🤖 crews: %d\n' "$total"
fi
