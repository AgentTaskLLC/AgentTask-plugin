---
name: agent-task-progress
description: How to keep an Agent Task ticket alive while you work — post periodic progress comments, record a PR URL when a coding task opens a PR, and confirm with the user before flipping status to done. Use during any sustained work on a claimed task, and whenever a pull request is created for a task.
---

# Agent Task — progress & PR-link behavior

Keep the ticket a faithful, live record of the work without nagging the user. Read the
`agent-task-workflow` skill for the tool surface.

## Periodic progress comments

While actively working a claimed task, post a short progress comment at meaningful checkpoints —
not on a noisy fixed timer. Good triggers:

- a sub-goal completed, a blocker hit or cleared, a decision made, or a long-running step finished;
- before you hand back to the user or pause for input.

Each comment (`add_comment` on the task) should be 1–3 lines: what changed, what's next, and any
blocker. Don't repeat unchanged status. If running under `/loop` or a similar timer, gate the
comment on "did something material change since the last one?" — skip the tick if not.

`add_comment` takes the **space's** `spaceUuid` plus `targetId` (the task/subtask UUID) and
`targetType` — passing the task UUID as `spaceUuid` fails with `space_not_found` (see
`agent-task-workflow`).

## Recording a PR

When a coding task produces a pull request:

1. Write the PR URL onto the task as soon as it exists: `update_task({ taskId, prUrl })`.
   (`prUrl` is validated as an http(s) URL.)
2. Mention it in the next progress comment.
3. Keep it current — if the PR is replaced, update `prUrl` again.

## Confirming completion (don't auto-close)

`done` is a meaningful state — never flip it silently. Before closing:

1. Check the work is actually captured (subtasks resolved, description current, PR linked).
2. If a PR is linked, confirm it's **merged** (not just open).
3. Ask the user: "everything captured and merged — close as done?"
4. On an explicit yes, `update_task({ status: done })` and post a final summary comment.

This is the same close-out `/finish` performs — use `/finish` for the full flow; use this skill's
guidance when you're mid-task and just keeping the ticket honest.
