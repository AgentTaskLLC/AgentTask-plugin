---
description: Personal daily standup — what you moved, what's in progress, and your blockers (read-only).
argument-hint: [optional: timeframe, e.g. "today" or "since friday"]
---

# /standup — your daily standup

A tight, personal "yesterday / today / blockers" for **you** (`assignee: "me"`). This command is
**read-only** — it never mutates tasks. Read the `agent-task-workflow` skill first.

Timeframe hint from the user: **$ARGUMENTS**

## Gather

- **Timeframe.** Default: since your last working day (treat a Monday run as "since Friday");
  honor `$ARGUMENTS` if it gives a range.
- `list_tasks_and_subtasks({ assignee: "me" })` — omit `spaceUuid` to span every space you're in
  (page through the cursor). Pull the latest `list_comments` on your in-progress items for status.
- Filter by date **client-side** (there's no server-side date filter): what moved to `done` in the
  window, what's `in_progress`, what's `isBlocked`, and your top `todo` items.

## Compose

Write a short, scannable standup (omit empty sections):

- **Done** — tasks you completed in the window (`AI-XX` + title).
- **In progress** — what you're actively on, each with a one-line "where it's at" from the latest
  comment.
- **Blocked** — `isBlocked` or stalled items, with the blocker if known.
- **Up next** — the 2–3 `todo` items you'd pick up next.

Keep it to codes + titles + one-liners — no walls of text. End by offering to post it as a comment
on a task/project or save it as a note (`/note`) if they want it persisted.
