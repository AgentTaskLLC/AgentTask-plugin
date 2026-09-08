---
description: Start the selected Agent Task ticket, or pick the next task when no ticket is specified.
argument-hint: "[task code, title, or description]"
allowed-tools: Read, Grep, Glob, mcp__plugin_agent-task_agent-task__fetch, mcp__plugin_agent-task_agent-task__search, mcp__plugin_agent-task_agent-task__list_spaces, mcp__plugin_agent-task_agent-task__list_projects, mcp__plugin_agent-task_agent-task__list_task_groups, mcp__plugin_agent-task_agent-task__list_labels, mcp__plugin_agent-task_agent-task__list_space_members, mcp__plugin_agent-task_agent-task__list_subtasks, mcp__plugin_agent-task_agent-task__start_work, mcp__plugin_agent-task_agent-task__create_task, mcp__plugin_agent-task_agent-task__create_subtask, mcp__plugin_agent-task_agent-task__update_task, mcp__plugin_agent-task_agent-task__update_subtask, mcp__plugin_agent-task_agent-task__add_comment
---

# Start work

Read `agent-task-workflow` first. Input: **$ARGUMENTS**.

1. Resolve explicit codes/URLs with `fetch`, titles with `search`. Keep the selected
   UUID as the target. If a project was named, inspect its tasks and choose work in
   that project; do not treat the project UUID as a task.
2. For empty input or a request to pick the next task, use `start_work` and validate
   its result against the requested scope. Stop on contention.
3. Reuse an existing task without overwriting its description, project, group,
   labels, or assignee merely to start it. Inspect its current claim. For new work,
   draft acceptance criteria, resolve the space and optional group/project/labels,
   then create once using the live schema and an idempotency key where supported.
4. Set only the needed fields on the selected UUID, including `in_progress` and
   execution provenance. Resolve an explicit member for API-key authentication;
   `"me"` is OAuth-only. Preserve existing assignments unless a change is requested.
   A status update alone does not prove an exclusive claim was acquired.
5. Never follow this with an untargeted `start_work` call: it can resume another
   ticket. Stamp provenance directly on writes to the selected task.
6. Continue the authorized work. Use the branch-link, subtask-execution, and
   progress skills. Record a PR URL when a PR is actually created.

Report the selected code, title, scope, and actual claim/status result.
