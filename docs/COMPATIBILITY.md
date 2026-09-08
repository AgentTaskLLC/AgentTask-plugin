# Harness compatibility

The portable contract is the hosted Streamable HTTP MCP service plus shared
`SKILL.md` instructions. Native commands, hook events, agent definitions, and
credential interpolation are adapter details.

| Surface | Claude Code | Codex | Cursor / VS Code | Other MCP clients |
| --- | --- | --- | --- | --- |
| MCP tools | Bundled OAuth connection | Bundled OAuth connection | Generated user config | Configure endpoint natively |
| Shared skills | Native discovery | Native discovery | Load with supported skill mechanisms | Explicit references where supported |
| Workflow entry points | Namespaced slash commands | Natural language via command skill | Shared procedures | Shared procedures |
| Restricted reporter | Bundled native subagent | Reporting skill; native restrictions required for isolation | Same limitation | Same limitation |
| Crew references | Portable JSON plus optional native agent | Portable JSON | Portable JSON | Reference data |
| Lifecycle ticket hint | Bundled SessionStart hook | Same hook on compatible versions, after trust review | No adapter claimed | None |
| Git pre-push reminder | Optional Bash script | Same script | Same script | Independent of MCP client |
| Crew status line | Optional Claude JSON adapter | Not supported by this adapter | Not supported by this adapter | None |
| Recurring work | User-requested native scheduler | User-requested native scheduler | Discover native support | Discover native support |

Skill discovery conventions vary by client and version. Keep the entire
`plugins/agent-task/` bundle together: skills use relative references to command
procedures and supporting files. For manual loading, start with
`skills/agent-task-workflow/SKILL.md` and then the relevant specialized skill.
Copying only an individual `SKILL.md` breaks those references.

The repository does not install or reconfigure a user's global skills, scheduler,
or tool permissions. Commands do not pin a model. Server-authored model/runtime
preferences remain subject to the user's choice and actual host support.

Current Codex [hook documentation](https://learn.chatgpt.com/docs/hooks) specifies
default discovery of `hooks/hooks.json`, a compatible `CLAUDE_PLUGIN_ROOT`
variable, and the same SessionStart `cwd` payload. This bundle uses that shared
format. Installation does not grant hook trust; older versions or disabled hooks
may not run it. The separate status-line adapter remains Claude-specific.

## Validation level

Repository checks cover manifest structure, skill/frontmatter parsing, local
Markdown links, default endpoint/auth, adapter metadata drift, credential-reference
generation, and shell behavior in temporary repositories. CI targets macOS/Linux.
Native Claude validation and the bundled Codex validator can additionally validate
installed CLI schema compatibility.

This does not certify live OAuth across every client, prove prompt-injection
resistance, or equate Markdown tool lists with native restrictions. Record concrete
client/version and authentication evidence before claiming an end-to-end integration.
