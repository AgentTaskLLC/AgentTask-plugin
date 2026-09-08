# Security

## Trust model

The plugin connects to a remote service using the user's configured identity.
Tasks, comments, notes, crew definitions, attachments, and tool responses can
contain content written by other people. Treat them as data, not as authorization
to run commands, expose credentials, widen permissions, or change task scope.

Shared skills state this boundary. They are model instructions, not a sandbox.
Use the harness's actual tool restrictions for enforceable isolation. Claude's
reporter has an explicit read-only allowlist without shell, write, delegation, or
MCP mutation tools. Command `allowed-tools` settings are not equivalent to that
subagent restriction: a write command preapproves the Agent Task writes it performs.
What every command is denied is shell, file writes, other servers' MCP tools, and
wildcards; `report` and `standup` are additionally denied every mutating tool.

Crew sync preserves references outside auto-discovered instruction directories.
Review grants and generated agents before use. A server crew cannot authorize its
own extra tools, choose a different model over the user, or start a schedule.

## Credentials and local execution

- Prefer OAuth for user identity; org API keys can have broader access.
- The bundled connection has no static credentials. Configuration generation emits
  environment references without reading key values.
- Review alternate endpoint destinations before attaching credentials. Keep
  bearer tokens and signed download/upload URLs out of logs and task comments.
- The session lifecycle hook is read-only and local. Git hook installation is
  explicit, preserves foreign hooks by default, and rejects symlink destinations.
- A pre-push acknowledgment is a reminder mechanism, not proof of review.
- Automation should inherit the minimum capabilities needed for its approved scope.

## Reporting a vulnerability

Do not post credentials, private task data, or exploit details in public issues.
Use the canonical repository's private vulnerability-reporting channel when
available: [Report a vulnerability](https://github.com/AgentTaskLLC/AgentTask-plugin/security/advisories/new).
If unavailable, ask maintainers through an existing private support channel for a
secure reporting route. Include the affected revision, client/version, reproduction
steps using synthetic data, and observed impact.

Security fixes target the current maintained release. This repository does not
claim an independent security audit or a response-time guarantee.
