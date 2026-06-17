# Connect Claude to Agent Task

This guide walks you through connecting **Claude Desktop** or **Claude.ai** to your Agent Task
workspace so Claude can read and update tasks over the Model Context Protocol (MCP).

For protocol and API details, see also:

- [`MCP_SERVER.md`](./MCP_SERVER.md) — endpoint, tools, scopes, API-key auth
- [`MCP_OAUTH.md`](./MCP_OAUTH.md) — OAuth flow (Claude Desktop)

You can also open **Settings → Connectors** in the app for the same endpoint URL, scope table,
and connect steps.

---

## Before you start

### 1. Confirm your deployment is ready

Your administrator must enable the MCP server on the API service:

```bash
MCP_SERVER_ENABLED=true
```

For **OAuth** sign-in (recommended for Claude Desktop), both flags are required:

```bash
MCP_SERVER_ENABLED=true
MCP_OAUTH_ENABLED=true
```

If these are not set, the MCP endpoint returns `404` or OAuth discovery fails.

### 2. Note your app URL

You need the public origin users open in the browser, for example:

```
https://tasks.yourcompany.com
```

The MCP endpoint is always:

```
https://<your-app-host>/v1/public/mcp
```

This must match `NEXT_PUBLIC_APP_URL` on the frontend. For OAuth, the host must be reachable
over **HTTPS** in production (Claude Desktop will not complete discovery against a broken or
mismatched origin).

### 3. Choose an auth method

| Method | Best for | Who sets it up |
|---|---|---|
| **OAuth** (recommended) | Claude Desktop, Claude.ai custom connector with browser login | Each user signs in with their Agent Task account |
| **API key** (`amk_…`) | Scripts, automation, clients that cannot run a browser OAuth flow | Org admin creates a key; user pastes it into the client |

**OAuth:** writes are attributed to **you** and limited to spaces you belong to.

**API key:** writes are attributed to the **key** (org-level); the key can access any space in
the organization (within granted scopes).

---

## Option A — Claude Desktop (OAuth, recommended)

### Step 1 — Open Claude Desktop connector settings

1. Open **Claude Desktop**.
2. Go to **Settings** (gear icon).
3. Open **Connectors** (or **Integrations**, depending on your Claude version).
4. Click **Add custom connector** (or **Add connector**).

### Step 2 — Enter the MCP URL

In the connector URL field, paste your MCP endpoint:

```
https://<your-app-host>/v1/public/mcp
```

Example:

```
https://tasks.yourcompany.com/v1/public/mcp
```

Do **not** add a path suffix or trailing slash beyond `/v1/public/mcp`.

### Step 3 — Let Claude discover OAuth

Claude calls the endpoint, receives a `401` with OAuth discovery metadata, registers as an MCP
client, and opens your browser. No manual client ID or secret is required on your side.

### Step 4 — Sign in to Agent Task

1. If you are not logged in, you are redirected to the Agent Task **login** page.
2. Sign in with your normal account.
3. You are returned to the **consent** screen listing the scopes Claude is requesting.

### Step 5 — Choose spaces and approve scopes

Review the permissions (for example `tasks:read`, `tasks:write`, `comments:write`).

Under **Spaces this connection can access**, tick the space(s) you want the connection to
reach. **At least one space is required.** The token is confined to the spaces you select: any
tool call against a space you did not select returns `space_not_found` (as if it does not
exist), and `list_spaces` shows only your selected spaces. To change the set later, reconnect
and re-authorize.

Click **Allow access**.

Claude receives an access token and connects. You should see Agent Task tools appear in the
connector list.

> **OAuth scope is per-space (no backward compatibility).** Tokens issued before this change
> were invalidated; existing connections must re-authorize and pick spaces. Organization API
> keys (`amk_…`) are unaffected and remain organization-wide.

### Step 6 — Verify with a read tool

In a new Claude chat, ask something like:

> List my todo tasks in space `<space-uuid>`.

Claude should call `list_spaces` or `list_tasks`. If you do not know a space UUID yet, ask:

> List the spaces in my organization.

Copy a `spaceUuid` from the result for later steps.

### Step 7 — Verify with a write tool (optional)

Ask Claude to make a small, reversible change, for example:

> Mark task `<task-uuid>` as in progress.

Claude will ask for **approval** before running write tools. Approve the tool call and confirm
the task updated in Agent Task.

### Step 8 — Disconnect (when needed)

In Claude Desktop → **Settings → Connectors**, disconnect the Agent Task connector. You can
also revoke tokens server-side via `POST /v1/public/oauth/revoke` (see [`MCP_OAUTH.md`](./MCP_OAUTH.md)).

---

## Option B — Claude.ai with an API key

Use this when OAuth is disabled or you prefer a static org key.

### Step 1 — Create an API key (admin)

1. Sign in as an **organization admin**.
2. Go to **Admin → Connectors → API**.
3. Click **Create API key**.
4. Name the key (for example `Claude MCP`).
5. Grant the scopes you need:

   | If you want to… | Enable these scopes |
   |---|---|
   | List and read tasks | `tasks:read` |
   | Create or update tasks | `tasks:write` |
   | Read subtasks | `subtasks:read` |
   | Create subtasks | `subtasks:write` |
   | Add comments | `comments:write` |

6. Copy the key (`amk_…`) immediately — it is shown only once.

### Step 2 — Add the connector in Claude.ai

1. Open [Claude.ai](https://claude.ai).
2. Go to **Settings → Connectors** (or **Integrations**).
3. Add a **custom** or **remote MCP** connector.
4. Set the URL to:

   ```
   https://<your-app-host>/v1/public/mcp
   ```

5. Add an HTTP header:

   | Header | Value |
   |---|---|
   | `Authorization` | `Bearer amk_…` (paste your full key) |

6. Save the connector.

### Step 3 — Confirm tools are listed

Claude runs `initialize` and `tools/list`. You should see **13 tools**, grouped into read-only
and write tools. If the list is empty or calls fail with `forbidden_scope`, edit the key scopes
in Admin and recreate the connector.

### Step 4 — Run your first commands

Same as OAuth verification:

1. **Read:** “List spaces in my organization” → `list_spaces`
2. **Read:** “List todo tasks in space `<uuid>`” → `list_tasks`
3. **Write:** “Create a task titled … in space `<uuid>`” → `create_task` (requires approval)

Entities are identified by **UUID**, not numeric IDs. Use `search` / `list_*` to find UUIDs,
and `fetch` to get full detail by UUID or app URL.

---

## Quick reference — useful tools

| Goal | Tool | Example argument |
|---|---|---|
| Find your spaces | `list_spaces` | — |
| List tasks | `list_tasks` | `spaceUuid?`, `status?`, `assignee?` ("me") |
| Search everything | `search` | `query` (+ optional `type`, `spaceUuid`) |
| Get one entity | `fetch` | `ref` (UUID or app URL) |
| Update a task | `update_task` | `taskId` + any of `status`/`priority`/`assignee`/`labels`/… |
| Bulk update tasks | `update_task` | `items: [{ taskId, … }]` (≤50) |
| List labels | `list_labels` | `spaceUuid` |
| Add a comment | `add_comment` | `spaceUuid`, `targetType`, `targetId`, `content` |
| Create a task | `create_task` | `spaceUuid`, `title` (or `items[]` for a batch) |

`assignee` accepts `"me"`, a username, an email, or a numeric user id.

**Status values:** `backlog`, `todo`, `in_progress`, `done`, `canceled`, `duplicate`

**Priority values:** `low`, `medium`, `high`, `urgent`

---

## Make ticket-first the default

You can have Claude **automatically** track work as tickets — starting from a ticket and
keeping it updated — without asking each time.

- **Easiest:** if the server runs with `MCP_TICKET_FIRST_ENABLED=true`, the connector already
  advertises this as a standing instruction on connect; nothing to configure.
- **For clients that don't apply server instructions** (or to customize it), paste this into
  your Claude **Project / connector custom instructions**:

  > Before starting any substantial task, call `start_work` first and work off the ticket it
  > returns. If its `action` is `resumed` or `picked_up`, continue that ticket — do not create a
  > duplicate. Set the ticket to in_progress when you begin and done when finished
  > (`update_task`), and record meaningful progress as comments (`add_comment`). Skip this for
  > trivial questions that involve no real work.

- **As a reusable skill (Claude.ai / Claude Code):** install the bundled skill at
  [`docs/skills/agent-task-ticket-first/SKILL.md`](skills/agent-task-ticket-first/SKILL.md).
  It triggers on substantial work and drives the same ticket-first flow (start_work →
  route group/project → keep updated). A skill applies to Claude-family clients that load
  skills; it complements — does not replace — the server instructions for other MCP clients.

No re-authorization is needed — this changes behavior only, not scopes.

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Connector URL not found / 404 | `MCP_SERVER_ENABLED` is off | Ask admin to enable the flag and restart the API |
| OAuth browser step never appears | `MCP_OAUTH_ENABLED` is off | Enable OAuth flag or use API-key method |
| `401 unauthorized` | Missing or wrong token / key | Reconnect OAuth or check `Authorization: Bearer amk_…` header |
| `forbidden_scope` | Key or token lacks scope | Add scopes on the API key or re-consent with broader scopes |
| `space_not_found` | Wrong space UUID, or (OAuth) you are not a member | Run `list_spaces`; use a space you belong to |
| `not_found` on a task | Wrong task UUID or task in another space | Run `list_tasks` in that space first |
| `rate_limited` | Too many requests | Wait for `Retry-After` and retry |
| Discovery fails on localhost | Claude needs a stable HTTPS origin in prod | Use a tunnel (ngrok, etc.) with HTTPS for local OAuth QA |

---

## What Claude can and cannot do (v1)

- **Can:** list spaces and tasks, read details, update fields, add comments, create tasks and subtasks.
- **Cannot:** delete tasks, attach files, or use MCP resources/prompts (tools only).
- **Writes** appear in the audit log and trigger the same notifications as the public REST API.

---

## Checklist

- [ ] `MCP_SERVER_ENABLED=true` on the API
- [ ] (Claude Desktop) `MCP_OAUTH_ENABLED=true` on the API
- [ ] MCP URL is `https://<host>/v1/public/mcp`
- [ ] (API key path) Admin created `amk_…` with required scopes
- [ ] `list_spaces` or `list_tasks` succeeds in Claude
- [ ] One write tool succeeds with approval (optional)
