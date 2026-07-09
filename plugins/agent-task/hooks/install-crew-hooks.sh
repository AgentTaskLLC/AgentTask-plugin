#!/usr/bin/env bash
# Agent Task — install / uninstall / status for the crew pre-push hook (AI-1207).
# Deterministic installer invoked by the `/crews hook` command (or run directly).
#
# Usage:
#   install-crew-hooks.sh install [--blocking] [--no-backup] [--force]
#   install-crew-hooks.sh uninstall
#   install-crew-hooks.sh status
#
# Only ever touches a pre-push hook that carries the Agent Task marker (unless --force),
# so a hook installed by another tool is never clobbered silently.
set -euo pipefail

MARKER="agent-task-crew-hook"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/pre-push"

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

hooks_dir() {
  local d
  d="$(git rev-parse --git-path hooks 2>/dev/null)" || die "not inside a git repository"
  mkdir -p "$d"
  printf '%s\n' "$d"
}

is_ours() { [ -f "$1" ] && grep -q "MARKER: $MARKER" "$1" 2>/dev/null; }

cmd_install() {
  local blocking=false backup=true force=false
  for arg in "$@"; do
    case "$arg" in
      --blocking) blocking=true ;;
      --no-backup) backup=false ;;
      --force) force=true ;;
      *) die "unknown option: $arg" ;;
    esac
  done
  [ -f "$TEMPLATE" ] || die "hook template missing: $TEMPLATE"

  local dir target
  dir="$(hooks_dir)"
  target="$dir/pre-push"

  if [ -e "$target" ] && ! is_ours "$target"; then
    if [ "$force" != true ]; then
      die "a non-Agent-Task pre-push hook already exists at $target (use --force to overwrite, or --no-backup to skip the backup)"
    fi
    if [ "$backup" = true ]; then
      cp "$target" "$target.backup.$(git rev-parse --short HEAD 2>/dev/null || echo bak)"
      echo "backed up existing hook → $target.backup.*"
    fi
  fi

  # Bake the default blocking mode into the template's placeholder.
  sed "s/__DEFAULT_BLOCKING__/$blocking/" "$TEMPLATE" > "$target"
  chmod +x "$target"
  echo "installed Agent Task pre-push hook (blocking default: $blocking) → $target"
}

cmd_uninstall() {
  local dir target
  dir="$(hooks_dir)"
  target="$dir/pre-push"
  if [ ! -e "$target" ]; then echo "no pre-push hook installed."; return 0; fi
  if ! is_ours "$target"; then die "pre-push hook at $target was not installed by Agent Task; leaving it untouched."; fi
  rm -f "$target"
  echo "removed Agent Task pre-push hook."
}

cmd_status() {
  local dir target
  dir="$(hooks_dir)"
  target="$dir/pre-push"
  if [ ! -e "$target" ]; then echo "pre-push: not installed"; return 0; fi
  if is_ours "$target"; then
    local mode
    mode="$(grep -m1 '^BLOCKING=' "$target" | sed 's/.*:-\(.*\)}.*/\1/' || true)"
    echo "pre-push: installed by Agent Task (blocking default: ${mode:-unknown})"
  else
    echo "pre-push: present but managed by another tool (not Agent Task)"
  fi
}

case "${1:-}" in
  install) shift; cmd_install "$@" ;;
  uninstall) cmd_uninstall ;;
  status) cmd_status ;;
  *) die "usage: install-crew-hooks.sh <install [--blocking] [--no-backup] [--force] | uninstall | status>" ;;
esac
