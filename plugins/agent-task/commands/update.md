---
description: Sync the board with reality — capture untracked work, describe + label it, map to group/project, and post status-update comments.
argument-hint: '[optional: scope hint, e.g. "this project" or "everything"]'
allowed-tools: Read, Grep, Glob, mcp__plugin_agent-task_agent-task__list_spaces, mcp__plugin_agent-task_agent-task__list_projects, mcp__plugin_agent-task_agent-task__list_task_groups, mcp__plugin_agent-task_agent-task__list_labels, mcp__plugin_agent-task_agent-task__list_space_members, mcp__plugin_agent-task_agent-task__list_tasks_and_subtasks, mcp__plugin_agent-task_agent-task__suggest_group, mcp__plugin_agent-task_agent-task__create_task, mcp__plugin_agent-task_agent-task__create_subtask, mcp__plugin_agent-task_agent-task__create_label, mcp__plugin_agent-task_agent-task__update_task, mcp__plugin_agent-task_agent-task__update_subtask, mcp__plugin_agent-task_agent-task__add_comment
---

# /update — make the board reflect the work

Mid-session sync. Walk the work that's actually happening and make AgentTask match it: capture
anything untracked, fill in the gaps, and post a status update. Be autonomous; confirm only the
side-effectful, non-obvious changes. Read the `agent-task-workflow` skill first.

Scope hint from the user: **$ARGUMENTS**

## Steps

1. **Confirm scope.** Decide whether to sync just *this session's work* or a whole project/space.
   If `$ARGUMENTS` makes it clear, proceed; otherwise ask once (default: this session's work).
2. **Inventory current state.** For the scope, `list_tasks_and_subtasks` (filter by space / project
   / group; it includes subtasks) to see what already exists.
3. **Capture untracked work.** For meaningful work happening that isn't tracked, create it:
   `create_task` for new top-level items, `create_subtask` for pieces of an existing task. Batch
   creates with `items[]` where possible.
4. **Fill the gaps** on every touched item:
   - **Description** — write a real one where it's missing or stale.
   - **Labels** — `list_labels`, apply fitting labels; `create_label` for clearly-useful missing
     ones. Apply labels to **subtasks** too (`update_subtask({ labels })`).
   - **Group + project** — map each item via `update_task({ groupUuid, projectUuid })`; use
     `suggest_group` (or group `description`s) as routing hints.
   - **Assignee** — preserve existing assignments. For requested changes, resolve a member;
     `assignee: "me"` requires OAuth and is unsupported with org API keys.
   - **Status** — advance obvious ones (e.g. clearly-started → `in_progress`). For anything
     non-trivial, **flag it** rather than silently flipping.
5. **Record PR links.** If a coding task has an open PR, set `update_task({ prUrl })`.
6. **Post status updates.** `add_comment` on each touched task with a short, specific progress note
   (what changed, what's next). Prefer batched `update_task({ items })` for the field changes.

## Report

Summarize: what you captured, what you re-labeled/mapped, which statuses you advanced, and a short
list of items you flagged for the user to confirm a status change on.
