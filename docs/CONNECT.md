# Connect AgentTask

The production MCP endpoint is `https://app.agent-task.com/v1/public/mcp`, using
Streamable HTTP. The bundled configuration contains this literal URL and no
Authorization header. It is shared by both plugin adapters.

## OAuth

Use OAuth for interactive user identity and the spaces approved during consent.
Install the Claude Code or Codex package using the [README](../README.md), then
authenticate through the client's MCP controls. Client policy and deployment
configuration can affect OAuth availability.

For a tools-only Codex connection without installing the plugin:

```sh
codex mcp add agent-task --url https://app.agent-task.com/v1/public/mcp
codex mcp login agent-task
```

For tools-only Claude Code:

```sh
claude mcp add --transport http --scope user agent-task https://app.agent-task.com/v1/public/mcp
```

Avoid duplicate connections when the plugin already supplies this endpoint.

## API keys and alternate endpoints

Org API keys are intended for automation and can have broader organizational
access than a user OAuth token. Resolve an explicit member UUID/username/email
for assignment; `assignee: "me"` requires OAuth. Never infer a user from a key.

Keep keys in the client's credential facility or process environment. Do not put
key values in shell arguments, repository files, task comments, or screenshots.
Do not hand-edit the installed plugin cache.

Generate client-specific configuration using **Python 3.11+**:

```sh
python3 scripts/mcp_config.py --client claude --auth api-key
python3 scripts/mcp_config.py --client codex --auth api-key
python3 scripts/mcp_config.py --client cursor --auth api-key
python3 scripts/mcp_config.py --client vscode --auth api-key
```

These commands print configuration fragments for review; they never read the
API-key value, modify client settings, or contact a server. Merge the result into
user-owned configuration, preserving other servers:

| Client | Configuration | Credential reference |
| --- | --- | --- |
| Claude Code | User/local MCP server settings or a reviewed MCP config file | `${AGENT_TASK_API_KEY}` |
| Codex | User `config.toml` | `bearer_token_env_var` |
| Cursor | User `~/.cursor/mcp.json` | `${env:AGENT_TASK_API_KEY}` |
| VS Code | User MCP configuration, or reviewed `.vscode/mcp.json` | `${env:AGENT_TASK_API_KEY}` |

For Codex API-key setup, after setting the environment securely:

```sh
codex mcp add agent-task --url https://app.agent-task.com/v1/public/mcp --bearer-token-env-var AGENT_TASK_API_KEY
```

Use `--auth oauth` (the default) for header-free configuration. To target another
deployment, pass `--url https://your-approved-host/v1/public/mcp` or set
`AGENT_TASK_MCP_URL` when running the generator. It rejects credential-bearing
URLs, interpolation, query strings, fragments, and non-loopback plaintext HTTP.
Choose the destination explicitly before attaching credentials.

The generator consumes `AGENT_TASK_MCP_URL`; the installed shared `.mcp.json`
does **not** expand it. Configure a user-owned connection for alternate hosts and
disable duplicate bundled connections through your client's supported controls.
If a client cannot override the bundled server, use MCP-only setup and load the
shared skills explicitly. Do not assume another client's interpolation syntax works.

Claude Code supports sensitive plugin `userConfig` values, but a static optional
Bearer header would interfere with the header-free OAuth default. This release
uses separate user-owned auth profiles; it does not advertise a plugin API-key
dialog or install a shell credential helper.

## Verify the connection

1. Inspect the endpoint shown by the client (`/mcp`, `claude mcp get agent-task`,
   or `codex mcp get agent-task` for a manually named server). Avoid sharing output
   that includes credential configuration.
2. Authenticate against that host, then invoke `list_spaces` as a read-only test.
3. Fetch a known entity and verify its organization/space. An entity's returned
   web URL alone does not prove which MCP host handled the connection.
4. Discover available tools. A missing family can reflect deployment, plan,
   credential, or client restrictions; a fixed count is not a health check.

The repo defaults and generated formats are tested locally. End-to-end OAuth
consent and authenticated operations must be verified in each target client.
An installed plugin cache or a separately configured connector may still point
at a different host from this checkout.

## Client references

- [Claude MCP configuration](https://code.claude.com/docs/en/mcp)
- [Claude plugin configuration](https://code.claude.com/docs/en/plugins-reference)
- [Codex plugins](https://learn.chatgpt.com/docs/plugins)
- [Cursor MCP configuration](https://prod.cursor.com/docs/mcp)
- [VS Code MCP configuration](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
