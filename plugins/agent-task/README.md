# Agent Task — Claude plugin

One install wires up the whole Agent Task experience in your agent:

- **MCP connection** — auto-connects to the Agent Task MCP server (`/v1/public/mcp`), so all
  the task/project/group/label/note/comment tools are available with no manual setup.
- **Intent-level slash commands** — smart, autonomous workflows that ask a few scoped
  (skippable) questions and then orchestrate the MCP tools for you:

  | Command | What it does |
  |---------|--------------|
  | `/start` | Start one task: map it to project + group, write a description, apply labels, claim it, set in-progress. |
  | `/plan` | Break a task into well-formed subtasks with descriptions, then claim the first piece. |
  | `/update` | Mid-session sync: capture untracked work, describe + label it (incl. subtasks), map to group/project, post status-update comments. |
  | `/triage` | Process the Inbox / unsorted tasks: route each to a group + project, label, set priority, flag duplicates. |
  | `/standup` | Personal daily: what you moved, what's in progress, and your blockers (read-only). |
  | `/report` | Ask date range / space / project, then write a full progress report (read-only). |
  | `/organize` | Reorganize tasks in a chosen scope into a coherent structure (groups, projects, labels). |
  | `/note` | Capture a note (decision, meeting, spec) in a space and link the related tasks. |
  | `/init` | Stand up a new project via Q&A: type, milestones, health, priority, optional seed groups + tasks. Also scaffolds a project `CLAUDE.md` so agents keep tickets updated. |
  | `/finish` | Close out: resolve subtasks, post a summary, confirm the PR is merged, set done. |

- **Skills** — behavioral knowledge the commands (and your agent) draw on automatically:

  | Skill | What it covers |
  |-------|----------------|
  | `agent-task-workflow` | Foundation: address-by-UUID, resolving `AI-XX` codes, the tool catalog, enum sets, lookup order, gotchas. |
  | `agent-task-progress` | Keep a ticket a live record: progress comments at checkpoints, record the PR URL, confirm before closing. |
  | `agent-task-branch-link` | Map git branches/PRs/commits ↔ tickets: derive the active ticket from the branch, name branches after it, keep `prUrl` synced. |
  | `agent-task-subtask-execution` | Drive multi-step work as subtasks: decompose, tick each done as you go, comment at milestones. |

## Install

The plugin is self-contained — it only talks to the hosted MCP server and ships **none** of the
Agent Task product source, so it can be distributed independently of this repo. There are three
ways to get it.

### A. From this product repo (this repo doubles as a marketplace)

```text
/plugin marketplace add alireza1220/Agent_task_management
/plugin install agent-task@agent-task
```

(Use `…@<branch>` until the plugin is on the default branch.)

### B. From a dedicated plugin repo (share without exposing the product source)

Publish just the plugin as a standalone marketplace repo (the `plugins/agent-task/` folder plus a
root `.claude-plugin/marketplace.json`). Recipients then run:

```text
/plugin marketplace add <owner>/agent-task-plugin
/plugin install agent-task@agent-task
```

Make that repo private and add collaborators, or public — the plugin carries no secrets (see
**Is it safe to make public?** below).

### C. From a local folder (no GitHub at all)

Hand someone the bundle as a folder or zip; they point at the local path:

```text
/plugin marketplace add /path/to/agent-task-plugin
/plugin install agent-task@agent-task
```

Restart Claude Code when prompted so the bundled MCP server connects.

Notes:
- For a **private** Git repo, normal git auth (`gh auth` / Keychain) covers interactive installs;
  for background auto-updates export a `GITHUB_TOKEN`.
- `/plugin marketplace update agent-task` pulls the latest; `/plugin` opens the interactive manager.

### Is it safe to make public?

Yes. The plugin contains no API keys or secrets (`.mcp.json` uses the `${AGENT_TASK_API_KEY}`
placeholder), no product source, and no internal infra references — only usage docs and a config
pointing at the hosted MCP endpoint. Every tool stays gated behind auth on the server, so a public
repo grants nobody access to data. Two things to weigh before publishing publicly:

1. The default `url` advertises the **dev** host. For a public artifact, prefer pointing
   `.mcp.json` (and the README URLs) at a **stable/prod** host instead.
2. Anyone can install it, but nobody can connect without an API key you issue or an OAuth login to
   your tenant — "public repo" ≠ "public access".

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
verify before pointing at a prod host). Full walkthrough: `docs/CONNECT_CLAUDE.md`.

### Option C — Cursor IDE OAuth (Cursor Desktop + Cloud Agents)

Cursor supports MCP servers via OAuth with specific redirect URIs. Agent Task now supports both:

| Cursor Surface | Redirect URI | Status |
|---------------|--------------|--------|
| **Cursor Desktop** | `cursor://anysphere.cursor-mcp/oauth/callback` | ✅ Supported |
| **Cursor Cloud Agents** | `https://www.cursor.com/agents/mcp/oauth/callback` | ✅ Supported |

**Setup:**

1. Add the MCP server to your Cursor settings (`~/.cursor/mcp.json`):

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

2. Cursor will initiate OAuth on first connection. A browser window opens for Agent Task login.
3. Select the spaces you want to connect, then consent.
4. Cursor Desktop uses the native `cursor://` protocol; Cloud Agents use the HTTPS callback.

**Note:** Cursor routes (slash commands/skills) are **not** supported — only MCP tools. For the full
Agent Task experience with commands, use Claude Code with this plugin.

### Pointing at another environment

To point at a different host, edit the `url` in `.mcp.json` (defaults to the dev host
`https://app.dev.agent-task.com/v1/public/mcp`).

## Automation (hooks) — optional

The commands and the `agent-task-progress` skill *prompt* the agent to keep tickets current. If you
want that **enforced** deterministically, add Claude Code hooks in your project's
`.claude/settings.json` (hooks run in the consuming repo, not the plugin):

- **Auto-record a PR on the active ticket** — a `PostToolUse` hook matching the `gh pr create` Bash
  call that writes the new PR URL onto the ticket derived from the current branch (see the
  `agent-task-branch-link` skill for branch → ticket resolution).
- **Surface the active ticket at session start** — a `SessionStart` hook that prints the `AI-XX`
  code embedded in the current branch, so the agent always knows which ticket to update.

Hooks are the right tool whenever you want "always do X when Y happens" rather than relying on the
model to remember. See the `update-config` skill / Claude Code hooks docs for the exact schema.

## Design

These commands are deliberately *intent-level*, not thin wrappers over single tools. Each one
resolves scope, reads current state, proposes a plan, confirms, executes via the MCP tools, and
reports. The shared conventions (address by UUID, resolve `AI-XX` codes, enum sets, lookup order)
live in `skills/agent-task-workflow`. Full design: `docs/mcp-smart-commands/design.md`.
