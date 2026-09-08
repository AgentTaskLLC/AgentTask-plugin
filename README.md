# Agent Task

Task, project, note, report, and crew workflows for MCP-capable coding agents.

The shared skills work across harnesses. This repository packages them for
**Claude Code and Codex**, and provides configuration for **Cursor, VS Code**, and
other Streamable HTTP MCP clients. Harness-specific features are documented
separately; an MCP connection alone does not install commands, skills, or agents.

Canonical repository: [AgentTaskLLC/AgentTask-plugin](https://github.com/AgentTaskLLC/AgentTask-plugin).
Personal forks and mirrors are development copies. The plugin is independent of
the Agent Task product source and connects to the hosted service.

## Install

Claude Code:

```text
/plugin marketplace add AgentTaskLLC/AgentTask-plugin
/plugin install agent-task@agent-task
```

For this local checkout, replace the marketplace source with its absolute path.
Open `/mcp` to authenticate. Use namespaced commands such as
`/agent-task:start AI-123` and `/agent-task:report`.

Codex, on versions with the plugin CLI:

```sh
codex plugin marketplace add /absolute/path/to/agent-task-plugin
codex plugin add agent-task@agent-task
```

Start a new session after installation. The local path is intentional while these
0.4.0 changes await release. Once published, the canonical GitHub source can be used
in the marketplace-add command. Do not install a second marketplace with the same
name without first inspecting your existing sources.

For MCP-only setup, authentication, endpoint overrides, and other harnesses, use
the [connection guide](docs/CONNECT.md) and [compatibility guide](docs/COMPATIBILITY.md).

## Included

- Shared workflow skills, including natural-language access to command procedures.
- Claude Code commands for start, plan, update, triage, standup, report, organize,
  note, init, finish, and crews.
- A Claude Code reporter with an explicit read-only tool allowlist.
- A local, read-only session hook that surfaces a branch ticket hint in Claude Code
  and compatible Codex versions after hook trust review.
- Optional Git pre-push reminders and an optional Claude crew status line.
- A configuration generator that emits credential references, never secret values.

The shipped connection is header-free OAuth at
`https://app.agent-task.com/v1/public/mcp`. API-key access and alternate endpoints
use user-owned client configuration. Tool availability comes from live discovery,
not a fixed tool count. See the [plugin reference](plugins/agent-task/README.md).

## Development

Python 3.11+ is used for repository checks and configuration generation. The
installed plugin has no Python or Node runtime requirement. Optional shell helpers
need Bash and Git 2.31+; session/status helpers also need jq.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
shellcheck plugins/agent-task/git-hooks/* plugins/agent-task/scripts/*.sh plugins/agent-task/statusline/*.sh
```

[Contributing](CONTRIBUTING.md) covers verification and release preparation.
[Security](SECURITY.md) explains trust boundaries and responsible reporting.
[Changelog](CHANGELOG.md) records compatibility changes.

## License

Proprietary. See [LICENSE](LICENSE). Copyright (c) 2025 Agent Task LLC.
