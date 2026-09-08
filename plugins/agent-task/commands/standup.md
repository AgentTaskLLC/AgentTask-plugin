---
description: Produce a read-only personal standup from task and activity evidence.
argument-hint: "[timeframe or member]"
allowed-tools: Task, mcp__plugin_agent-task_agent-task__fetch, mcp__plugin_agent-task_agent-task__search, mcp__plugin_agent-task_agent-task__list_spaces, mcp__plugin_agent-task_agent-task__list_projects, mcp__plugin_agent-task_agent-task__list_space_members, mcp__plugin_agent-task_agent-task__list_tasks_and_subtasks, mcp__plugin_agent-task_agent-task__list_subtasks, mcp__plugin_agent-task_agent-task__list_comments, mcp__plugin_agent-task_agent-task__list_day_log, mcp__plugin_agent-task_agent-task__get_day_deck
---

# Standup

Read `agent-task-workflow` and `agent-task-reporting`. Input: **$ARGUMENTS**.
Default to the last working day (Monday includes Friday). Resolve the member:
`"me"` works with OAuth; org API keys require an explicit member.

Gather current tasks and supported activity history, following cursors. Use the
bundled reporter when available and delegation is authorized. Keep completed,
in-progress, blockers, and next-work sections short. Never infer completion dates
from last-update timestamps or persist the result without a separate request.
