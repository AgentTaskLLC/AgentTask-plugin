---
name: agent-task-subtask-execution
description: Drive multi-step (especially coding) work as Agent Task subtasks — decompose the ticket, mark each subtask done as you finish it, and comment at milestones. Use during sustained execution of a claimed task.
---

# Agent Task — subtask-driven execution

Make the ticket mirror your actual execution so anyone watching sees real-time progress. Read
`agent-task-workflow` for the tools and `agent-task-progress` for the commenting cadence.

## Decompose first

After `start_work` (or `/start`) claims the ticket, break non-trivial work into **subtasks** before
diving in — use `/plan`, or `create_subtask({ spaceUuid, parentTaskId, title, description })` per
piece. Each subtask should be a single, checkable step with a clear "done." Skip this only for
genuinely one-step tasks.

## Tick them off as you go

- Mark a subtask `in_progress` when you start it and `update_subtask({ status: done })` the moment
  it's actually finished — not in a batch at the end. The subtask list is the live progress bar.
- Keep the **parent** honest: it stays `in_progress` while any subtask is open; don't flip the
  parent to `done` until the children are resolved (see `/finish`).
- Labels work on subtasks too — carry over the fitting ones from the parent.

## Comment at milestones, not every step

Post a short `add_comment` on the parent at meaningful checkpoints (a subtask group done, a blocker
hit/cleared, a decision) — 1–3 lines, what changed + what's next. Don't narrate every micro-step.

## Discoveries become subtasks

When execution surfaces new required work, add it as a subtask rather than silently expanding scope
or dropping it — the ticket should always reflect the true remaining work.

## Reporting execution state (claimed runs)

If you're running as a claimed/automated executor, report lifecycle with
`update_task_claim({ state })`: `in_progress` while working, `blocked` when you need input (post the
details via `add_comment`), and `completed` / `failed` at the end. This is the execution signal;
`update_subtask` / `update_task` remain the source of truth for the board itself.
