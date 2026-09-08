---
description: Close out completed work — resolve subtasks, post a summary, confirm the PR is merged, and set the task to done.
argument-hint: "[task code/title, or empty for the active task]"
allowed-tools: mcp__plugin_agent-task_agent-task__fetch, mcp__plugin_agent-task_agent-task__search, mcp__plugin_agent-task_agent-task__list_subtasks, mcp__plugin_agent-task_agent-task__list_space_members, mcp__plugin_agent-task_agent-task__update_subtask, mcp__plugin_agent-task_agent-task__update_task, mcp__plugin_agent-task_agent-task__add_comment
---

# /finish — wrap up a task

Close out a finished task cleanly. Confirm with the user before the final status flip — `done` is a
meaningful state. Read the `agent-task-workflow` skill first.

Input from the user: **$ARGUMENTS** (an `AI-XX` code / title, or empty for the active task).

## Steps

1. **Resolve the task.** Use `fetch` for a code/URL, or `search` for a title. If empty, read the
   active task from session context or listings; do not use `start_work` for a lookup.
   With an org API key, resolve an explicit member instead of `assignee: "me"`.
2. **Check subtasks.** `list_subtasks`. If any are unresolved, list them and ask whether to close
   them too (`update_subtask({ status: done })`) or leave them — don't silently close children.
3. **Coding task?** If it has a PR (`prUrl`) or should have one:
   - Make sure the PR URL is recorded (`update_task({ prUrl })`).
   - Confirm the PR is merged before closing. If it isn't merged, say so and ask whether to still
     close or wait.
4. **Post a summary.** `add_comment` with a concise close-out note: what was delivered, the PR link,
   and anything notable for whoever reads it later.
5. **Confirm + close.** Ask "everything captured and (if coding) merged — close as done?" On yes,
   `update_task({ status: done })`.

## Report

Confirm the task is done, with its code + title, the PR link if any, the closing summary you posted,
and the state of its subtasks.
