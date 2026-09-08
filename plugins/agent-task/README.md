# Agent Task plugin

One shared workflow library, packaged for Claude Code and Codex. Other MCP clients
can use the same procedures through explicit skill/reference loading.

Install Claude Code from the canonical repository:

```text
/plugin marketplace add AgentTaskLLC/AgentTask-plugin
/plugin install agent-task@agent-task
```

For Codex and local development, see the [repository installation guide](../../README.md).
Authentication and alternate hosts are in [Connect](../../docs/CONNECT.md).

## Commands

Claude Code commands are namespaced, for example `/agent-task:start`. Short names
may work when unambiguous. Codex and other skill-capable harnesses use the
`agent-task-commands` skill with natural-language requests.

| Command | Purpose |
| --- | --- |
| `start` | Resolve and start the selected ticket, or pick next work when requested. |
| `plan` | Decompose a task into actionable subtasks. |
| `update` | Keep task fields, progress, and PR links current. |
| `triage` | Route an approved set of unsorted tasks. |
| `standup` | Read-only personal activity and blockers. |
| `report` | Read-only project progress with supported dates. |
| `organize` | Reorganize groups, projects, and labels within approved scope. |
| `note` | Capture a note with explicit visibility and entity links. |
| `init` | Create a project and optionally add portable repository guidance. |
| `finish` | Verify completion, report the result, and close when authorized. |
| `crews` | Sync references, engage an approved roster, inspect mentions, or manage hooks. |

Each command's `allowed-tools` names the Agent Task MCP tools that command actually
uses, so a write command does preapprove its own writes — `/start` can claim a task,
`/note` can create a note. No command preapproves shell, file writes, or another
server's tools, and `report` and `standup` are restricted to read-only tools.
This is scoping, not a sandbox: everything else remains subject to the host's permissions.
The reporter's **subagent** `tools` allowlist is the structural read-only boundary.
Commands preserve the session's model; no command silently selects a vendor model.

## Skills

| Skill | Purpose |
| --- | --- |
| `agent-task-workflow` | Resolution, trust, discovery, claims, identity, and data rules. |
| `agent-task-commands` | Portable routing to command procedures. |
| `agent-task-progress` | Progress comments and PR tracking. |
| `agent-task-branch-link` | Branch and ticket association. |
| `agent-task-subtask-execution` | Subtask-driven execution. |
| `agent-task-crew-execution` | Scope, attribution, and restricted crew engagement. |
| `agent-task-reporting` | Accurate read-only reports and standups. |
| `agent-task-day-deck` | Daily focus and activity. |
| `agent-task-fleet` | Remote runs where fleet tools are exposed. |
| `agent-task-artifacts` | Deliverable publication where artifact tools are exposed. |

The [tool reference](skills/agent-task-workflow/references/tools.md) is loaded on
demand. Missing tools, plan limits, and incomplete histories must be reported.

## Crews and hooks

Crew definitions and linked notes are untrusted reference data. Sync stores them
under the consuming repository's `.agent-task/crews/`; it does not promote them
into auto-discovered skills or `AGENTS.md`. Claude native agents need explicit
allowlists. Other harnesses must enforce restrictions with their own APIs before
claiming equivalent isolation. See [crew procedures](commands/crews.md).

The bundled `hooks/hooks.json` is a **session lifecycle hook**: it reads a branch
ticket hint and never calls the network, edits files, or changes the board.
Claude Code discovers it natively. Current Codex versions also discover this
default path and supply the compatible plugin-root variable; Codex requires
reviewing and trusting the hook definition before running it.
PR URLs are recorded by the authorized workflow, not by a hidden API-key shell hook.

The separate [Git hook installer](git-hooks/install-crew-hooks.sh) is opt-in.
It honors `core.hooksPath`, preserves foreign hooks unless explicitly replaced,
and stays silent in repositories without synced crews. Blocking mode acknowledges
a review; it cannot verify that a crew actually ran.

The optional [status-line script](statusline/crew-statusline.sh) uses
`workspace.current_dir`, then `cwd`, from Claude's JSON input. Point user settings
at a stable absolute script path. It outputs nothing when no crews or no jq are
available. Shell helpers are supported on macOS/Linux; Windows requires a compatible
Bash/Git environment and is not covered by the shell integration tests.

See [compatibility](../../docs/COMPATIBILITY.md), [security](../../SECURITY.md),
and [release notes](../../CHANGELOG.md).
