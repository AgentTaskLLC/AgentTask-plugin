# Changelog

## 0.4.0 - Unreleased

### Added

- Native Codex manifest and repository marketplace alongside Claude Code.
- Portable command routing and dedicated reporting, DayDeck, fleet, and artifact skills.
- Client-specific OAuth/API-key configuration generation for Claude, Codex, Cursor, and VS Code.
- Read-only Claude reporter and local SessionStart ticket hint shared with compatible Codex versions.
- Structural validation, local link checks, shell regression coverage, and CI.
- Security, contribution, compatibility, and release documentation.

### Fixed

- Commands name the AgentTask MCP tools they call. Previously every command preapproved only
  `Read, Grep, Glob`, which left no command able to reach the MCP server it drives.
- `report` and `standup` allow `Task`, so the documented delegation to the bundled reporter can
  actually be authorized; both remain denied every mutating tool.
- Command tool validation enforces rules (deny shell, file writes, foreign MCP servers, wildcards;
  read-only commands deny mutating tools) instead of one frozen literal string. Scoped grants such
  as `Bash(...)` are matched on the tool name, so a narrowed grant cannot smuggle a denied tool past
  the check.
- CI shell prerequisite check fails on a missing tool and names it; `command -v a b c` exited 0 even
  when a tool was absent.
- Workflow skill line budget tracks the achieved size rather than the pre-split one.
- Git hook installer recognizes the 0.3.0 marker line, so upgrading no longer requires `--force` and
  `uninstall` no longer refuses the project's own hook.
- Repository scripts read and write with an explicit UTF-8 encoding rather than the platform locale.
- Malformed Markdown link tokens are reported per file instead of aborting validation.
- Live code/UUID resolution, OAuth-only member identity, task selection, and report dates.
- Tool discovery moved to on-demand references; no fixed live-tool count.
- Git hook silence, empty-repository gating, foreign-hook preservation, and unique backups.
- Status-line workspace selection and safe handling of invalid input.
- Canonical installation instructions and stale documentation links.

### Changed

- Git helpers moved from `hooks/` to `git-hooks/`; update direct script references.
  Existing installed Git hooks are not modified automatically: reinstall to adopt fixes.
- Crew data remains untrusted reference material; new sync procedures no longer
  promote linked notes into auto-discovered skills or inherit all execute-mode tools.
  Existing generated agents/skills require review; they are not silently rewritten.
- OAuth remains header-free. API-key and custom-host configuration is user-owned;
  the shared bundled endpoint does not interpolate environment variables.
- The Claude manifest is the version source; Codex metadata is generated and checked.

## 0.3.0

- Production endpoint, crew workflows, and marketplace metadata.

## 0.2.1

- Claim provenance and plugin metadata updates.
