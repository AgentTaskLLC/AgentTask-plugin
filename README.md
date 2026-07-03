# Agent Task — Claude plugin marketplace

A standalone, self-contained Claude Code plugin for **Agent Task**. Installing it wires up the
Agent Task MCP connection and adds intent-level slash commands (`/start`, `/update`, `/report`,
`/organize`, `/init`, `/finish`, `/crews`) plus the shared workflow skills — including **crew
personas** (assignable AI teammates) that `/crews sync` materializes as real Claude Code subagents
with enforced advise-mode tool restrictions.

This bundle is fully independent of the Agent Task product source — it only talks to the hosted
MCP server. You never need the product repo to use it.

## Install (Claude Code)

**From this repo** (once pushed to a Git host you can read):

```text
/plugin marketplace add <owner>/<repo>     # e.g. your-org/agent-task-plugin
/plugin install agent-task@agent-task
```

**From a local copy** (no GitHub needed — hand someone the folder/zip):

```text
/plugin marketplace add /path/to/agent-task-plugin
/plugin install agent-task@agent-task
```

Restart Claude Code when prompted so the bundled MCP server connects.

## Authenticate

The plugin connects to `https://app.dev.agent-task.com/v1/public/mcp`. Pick one:

- **OAuth** (per-user, space-scoped) — recommended for interactive use. Remove the `Authorization`
  header from `plugins/agent-task/.mcp.json` and the client runs a browser login + consent flow on
  connect.
- **Org API key** (org-wide) — export `AGENT_TASK_API_KEY=amk_…` before installing.

Full walkthrough: [`docs/CONNECT_CLAUDE.md`](docs/CONNECT_CLAUDE.md). Plugin details:
[`plugins/agent-task/README.md`](plugins/agent-task/README.md).

## What's inside

```
.claude-plugin/marketplace.json     # marketplace manifest (this repo IS the marketplace)
plugins/agent-task/                  # the plugin: .mcp.json, commands/, skills/, manifest
docs/CONNECT_CLAUDE.md               # end-user auth + connect guide
```

## Publishing updates

Bump `version` in both `.claude-plugin/marketplace.json` and
`plugins/agent-task/.claude-plugin/plugin.json`, commit, and push. Users get it via
`/plugin marketplace update agent-task`.
