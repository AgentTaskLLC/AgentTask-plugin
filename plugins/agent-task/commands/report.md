---
description: Write a full progress report — ask date range / space / project, then summarize the tasks (read-only).
argument-hint: [optional: timeframe, space, or project]
---

# /report — progress report

Generate a clear, structured progress report. This command is **read-only** — it summarizes, it
never mutates tasks. Read the `agent-task-workflow` skill first.

Hint from the user: **$ARGUMENTS**

## Clarify (skippable)

Ask only what isn't already implied by `$ARGUMENTS`; offer sensible defaults:

1. **Date range** — e.g. last week / this sprint / an explicit `YYYY-MM-DD .. YYYY-MM-DD`.
   Default: the last 7 days.
2. **Space** — only ask if the user has more than one (`list_spaces`). Otherwise use the single one.
3. **Project** — a specific project, or all projects in the space. Default: all.

## Gather

- `list_tasks_and_subtasks` for the scope (filter by `projectUuid` / `groupUuid` / `status` as
  chosen; omit `spaceUuid` to span every space). Page through `nextCursor` so the report isn't
  truncated. Pull `list_comments` (latest status notes) and `fetch` for any item you need in full.
- Filter to the chosen date range **client-side** on the returned items (created/updated/completed
  within it) — there's no server-side date filter.

## Compose

Write the report as markdown with these sections (omit any that are empty):

- **Summary** — 2–3 sentences: overall momentum in the period.
- **Completed** — tasks moved to `done` in the range (grouped by project/group).
- **In progress** — `in_progress` tasks, with the latest comment/status note.
- **Blocked / at risk** — `isBlocked` tasks or stalled ones; say why if known.
- **New / backlog** — notable items created in the range.
- **By project** (if multiple) — a one-line health line per project.

Keep it scannable: codes (`AI-XX`) + titles, short status notes, no walls of text. End by offering
to post it as a comment on a project/task or save it as a note if the user wants it persisted.
