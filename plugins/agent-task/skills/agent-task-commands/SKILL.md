---
name: agent-task-commands
description: Run Agent Task start, plan, update, triage, organize, note, init, finish, or crew workflows from natural-language requests in any harness.
---

# Workflow entry points

Read `agent-task-workflow`. Select just the relevant reference below.
In Claude Code these are namespaced slash commands. In other harnesses, read the
same Markdown procedure and use the user's natural-language request as its input
instead of `$ARGUMENTS`. Claude frontmatter describes that adapter; it does not
grant permissions or select models in another harness.

- [Start](../../commands/start.md): resolve and begin the selected ticket.
- [Plan](../../commands/plan.md): decompose existing work.
- [Update](../../commands/update.md): synchronize task progress.
- [Triage](../../commands/triage.md): route unsorted tasks.
- [Organize](../../commands/organize.md): restructure an approved scope.
- [Note](../../commands/note.md): capture and link a note.
- [Init](../../commands/init.md): initialize a project.
- [Finish](../../commands/finish.md): verify and close out completed work.
- [Crews](../../commands/crews.md): references, engagement, and optional hooks.

For reports and standups, use `agent-task-reporting` directly. Respect the user's
existing authorization; ask only when scope or a consequential choice is missing.
If a native capability is unavailable, state the limit and complete independent work.
