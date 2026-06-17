# Agent Task — Claude plugin

One install wires up the whole Agent Task experience in your agent:

- **MCP connection** — auto-connects to the Agent Task MCP server (`/v1/public/mcp`), so all
  the task/project/group/label/note/comment tools are available with no manual setup.
- **Intent-level slash commands** — smart, autonomous workflows that ask a few scoped
  (skippable) questions and then orchestrate the MCP tools for you:

  | Command | What it does |
  |---------|--------------|
  | `/start` | Start one task: map it to project + group, write a description, apply labels, claim it, set in-progress. |
  | `/update` | Mid-session sync: capture untracked work, describe + label it (incl. subtasks), map to group/project, post status-update comments. |
  | `/report` | Ask date range / space / project, then write a full progress report (read-only). |
  | `/organize` | Reorganize tasks in a chosen scope into a coherent structure (groups, projects, labels). |
  | `/init` | Stand up a new project via Q&A: type, milestones, health, priority, optional seed groups + tasks. |
  | `/finish` | Close out: resolve subtasks, post a summary, confirm the PR is merged, set done. |

## Install

This bundle is a self-contained Claude plugin **marketplace** (`.claude-plugin/marketplace.json` at
its root) — it does not require the Agent Task product repo. Install it in Claude Code one of two
ways:

**From a Git repo** (after you push this bundle to one):

```text
/plugin marketplace add <owner>/<repo>     # e.g. your-org/agent-task-plugin
/plugin install agent-task@agent-task
```

**From a local folder** (no GitHub needed):

```text
/plugin marketplace add /path/to/agent-task-plugin
/plugin install agent-task@agent-task
```

Then restart when prompted so the bundled MCP server connects.

Notes:
- For a **private** Git repo, your normal git auth (`gh auth` / Keychain) covers interactive
  installs; for background auto-updates export a `GITHUB_TOKEN`.
- `/plugin marketplace update agent-task` pulls the latest; `/plugin` opens the interactive manager.

## Setup

The MCP server supports **two auth modes** — pick one. The bundled `.mcp.json` ships with the
API-key mode (Option A).

### Option A — Org API key (default; best for headless/automation)

| Variable | Required | Purpose |
|----------|----------|---------|
| `AGENT_TASK_API_KEY` | **yes** | Your org API key (`amk_…`), sent as `Authorization: Bearer …`. |

Create an org API key in Agent Task (Settings → API keys), export it as `AGENT_TASK_API_KEY`,
then install the plugin. The key is read from your environment — it is **never** committed into
the plugin. This grants **org-wide** access and attributes actions to the key's creator.

### Option B — OAuth (per-user, space-scoped; best for interactive use)

The server also speaks OAuth (RFC 6749/8414/8707/7591/7009/9728) and is enabled on the dev host.
Instead of a static key you sign in via the browser and consent to specific spaces; the token
auto-rotates and is revocable. To use it, drop the `Authorization` header from `.mcp.json` so the
client runs the OAuth flow on connect:

```json
{
  "mcpServers": {
    "agent-task": {
      "type": "http",
      "url": "https://app.dev.agent-task.com/v1/public/mcp"
    }
  }
}
```

On connect the server returns `401` with a `WWW-Authenticate` discovery challenge; the client opens
the Agent Task login + consent screen (where you pick spaces), then connects with a per-user token.
No `AGENT_TASK_API_KEY` needed in this mode. (claude.ai / Claude Desktop: add the same URL as a
**custom connector** to get the OAuth flow — note that path delivers the MCP **tools only**, not the
slash commands/skills, which are part of this Claude Code plugin.)

OAuth requires `MCP_SERVER_ENABLED` + `MCP_OAUTH_ENABLED` on the target deployment (set on dev;
verify before pointing at a prod host). Full walkthrough: [`../../docs/CONNECT_CLAUDE.md`](../../docs/CONNECT_CLAUDE.md).

### Pointing at another environment

To point at a different host, edit the `url` in `.mcp.json` (defaults to the dev host
`https://app.dev.agent-task.com/v1/public/mcp`).

## Design

These commands are deliberately *intent-level*, not thin wrappers over single tools. Each one
resolves scope, reads current state, proposes a plan, confirms, executes via the MCP tools, and
reports. The shared conventions (address by UUID, resolve `AI-XX` codes, enum sets, lookup order)
live in `skills/agent-task-workflow`.
