#!/usr/bin/env bash
# Explicit installer for the optional, harness-independent crew reminder.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/pre-push"
temporary=""
trap 'if [ -n "$temporary" ]; then rm -f -- "$temporary"; fi' EXIT

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
# Recognizes the current marker line and the 0.3.0 one (which carried a trailing
# comment after the marker). Anchored so prose merely mentioning it does not match.
is_ours() {
  [ -f "$1" ] && grep -Eq '^# MARKER: agent-task-crew-hook([[:space:]].*)?$' "$1"
}

# Refuses to write through a symlink to an unintended target. Only the path itself
# is checked; benign symlinked ancestors (/tmp, /var/folders, a linked home) are fine.
reject_symlink() {
  [ ! -L "$1" ] || die "refusing symlink path: $1"
}

hooks_dir() {
  local root dir
  root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not inside a working repository"
  dir="$(git -C "$root" rev-parse --path-format=absolute --git-path hooks)" || die "cannot resolve hooks directory"
  reject_symlink "$dir"
  printf '%s\n' "$dir"
}

cmd_install() {
  local blocking=false backup=true force=false arg dir target saved
  for arg in "$@"; do
    case "$arg" in
      --blocking) blocking=true ;;
      --no-backup) backup=false ;;
      --force) force=true ;;
      *) die "unknown option: $arg" ;;
    esac
  done
  if [ "$backup" = false ] && [ "$force" != true ]; then
    die "--no-backup requires --force; it only controls backup creation"
  fi
  [ -f "$TEMPLATE" ] || die "hook template missing"
  dir="$(hooks_dir)"
  target="$dir/pre-push"
  reject_symlink "$target"
  [ ! -e "$target" ] || [ -f "$target" ] || die "pre-push is not a regular file"

  if [ -e "$target" ] && ! is_ours "$target"; then
    [ "$force" = true ] || die "foreign pre-push hook exists; --force replaces it with a backup (--no-backup only disables that backup)"
    if [ "$backup" = true ]; then
      saved="$(mktemp "$target.backup.XXXXXX")"
      cp -p -- "$target" "$saved"
      printf 'backed up existing hook: %s\n' "$saved"
    fi
  fi
  mkdir -p -- "$dir"
  temporary="$(mktemp "$dir/.agent-task-pre-push.XXXXXX")"
  sed "s/__DEFAULT_BLOCKING__/$blocking/" "$TEMPLATE" > "$temporary"
  chmod 755 "$temporary"
  mv -f -- "$temporary" "$target"
  temporary=""
  printf 'installed AgentTask pre-push hook (blocking: %s): %s\n' "$blocking" "$target"
}

cmd_uninstall() {
  local target
  target="$(hooks_dir)/pre-push"
  reject_symlink "$target"
  if [ ! -e "$target" ]; then printf 'pre-push: not installed\n'; return; fi
  is_ours "$target" || die "pre-push is managed by another tool; leaving it untouched"
  rm -- "$target"
  printf 'removed AgentTask pre-push hook; backups are preserved\n'
}

cmd_status() {
  local target
  target="$(hooks_dir)/pre-push"
  reject_symlink "$target"
  if [ ! -e "$target" ]; then
    printf 'pre-push: not installed\n'
  elif is_ours "$target"; then
    printf 'pre-push: installed by AgentTask\n'
  else
    printf 'pre-push: managed by another tool\n'
  fi
}

command_name="${1:-}"
if [ "$#" -gt 0 ]; then shift; fi
case "$command_name" in
  install) cmd_install "$@" ;;
  uninstall|status)
    [ "$#" -eq 0 ] || die "$command_name takes no options"
    "cmd_$command_name"
    ;;
  *) die "usage: install-crew-hooks.sh <install [--blocking] [--force] [--no-backup] | uninstall | status>" ;;
esac
