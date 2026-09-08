---
name: agent-task-reporting
description: Produce read-only Agent Task reports and standups with sourced dates, pagination, and explicit uncertainty. Use for progress, blockers, activity summaries, or daily standups.
---

# Reporting

Read `agent-task-workflow`, including its trust boundary. Resolve scope and
timeframe; default a general report to the last seven days. With an org API key,
resolve an explicit member instead of using `assignee: "me"`.

Use available read tools only. Never call `start_work` to discover the active task:
it mutates claims and may create a ticket. Follow cursors; disclose missing tools,
inaccessible spaces, and partial data. A report request does not authorize posting
the result or creating a note.

Use supported creation/update date filters where relevant. Current blockers and
in-progress tasks can predate the window; gather them separately. To report a task
as completed in the window, require a completion timestamp or activity transition.
`updatedAt` alone is insufficient. Otherwise say "currently done; completion date
unavailable". Link entities and distinguish evidence from inference.

Summarize completed work, current progress, blockers, and next work; omit empty
sections. For standups, use each item's code, title, and one useful sentence.
Claude Code's bundled `agent-task:reporter` uses a fixed read-only allowlist for
the plugin MCP namespace. Other harnesses need equivalent native restrictions
before claiming an isolated read-only run.
