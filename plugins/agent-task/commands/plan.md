---
description: Break a task into well-formed subtasks and begin execution when requested.
argument-hint: "[task code/title, or describe the work]"
allowed-tools: Read, Grep, Glob, mcp__plugin_agent-task_agent-task__fetch, mcp__plugin_agent-task_agent-task__search, mcp__plugin_agent-task_agent-task__list_subtasks, mcp__plugin_agent-task_agent-task__list_space_members, mcp__plugin_agent-task_agent-task__create_task, mcp__plugin_agent-task_agent-task__create_subtask, mcp__plugin_agent-task_agent-task__update_task, mcp__plugin_agent-task_agent-task__update_subtask, mcp__plugin_agent-task_agent-task__add_comment
---

# /plan — break a task into subtasks

Turn one task into an ordered set of **subtasks** small enough to execute and tick off. Propose the
breakdown, get a yes, then create it. Be opinionated about the decomposition but keep each piece
genuinely actionable. Read the `agent-task-workflow` skill first.

Input from the user: **$ARGUMENTS** (an `AI-XX` code / title, a rough description, or empty for the
active task).

## Steps

1. **Resolve the task.** From `$ARGUMENTS` (`fetch` for a code, `search` for a title), or if empty
   read the active task from session context or task listings. Do not mutate claims to look it up.
   If the input is new work with no task yet, create it first (`create_task`) or run
   `/start` — `/plan` operates on an existing task.
2. **Understand the work.** Read the task `description` and any relevant conversation/code context.
   `fetch` the task for the full body if needed.
3. **Draft the breakdown.** Propose 3–8 ordered subtasks, each with a one-line **description** and a
   clear "done" meaning. Aim for pieces a single sitting could finish; call out dependencies/order.
   Avoid noise (don't split a one-step task).
4. **Confirm.** Show the proposed subtasks as a numbered list; let the user add/remove/reorder.
   Skippable — if they say "just do it," proceed with your draft.
5. **Create.** `create_subtask({ spaceUuid, parentTaskId, title, description, labels })` for each
   (subtasks are created one at a time — no batch). Carry over fitting labels from the parent.
   Creating a subtask records an implicit claim on the **parent** (planning is working it), so stamp
   your execution context (`branch`, `worktreePath`, `hostname`, `os`, `sessionId`/`sessionName`) on
   these calls too — see the claim-provenance note in `agent-task-workflow`.
6. **Kick off** only when execution was requested. Set the parent `in_progress`, preserve existing
   assignments, and resolve an explicit member for org API keys (`"me"` is OAuth-only).
   Mark the first subtask `in_progress`. As you execute, mark each `update_subtask({ status: done })` when
   finished and comment at milestones (see `agent-task-subtask-execution`).

## Report

List the subtasks created (with the parent code + title), note which one you started on, and any
dependencies/order the user should know about.
