---
description: Produce a read-only progress report with accurate dates and explicit data gaps.
argument-hint: "[timeframe, space, or project]"
allowed-tools: Task, mcp__plugin_agent-task_agent-task__fetch, mcp__plugin_agent-task_agent-task__search, mcp__plugin_agent-task_agent-task__list_spaces, mcp__plugin_agent-task_agent-task__list_projects, mcp__plugin_agent-task_agent-task__list_space_members, mcp__plugin_agent-task_agent-task__list_tasks_and_subtasks, mcp__plugin_agent-task_agent-task__list_subtasks, mcp__plugin_agent-task_agent-task__list_comments, mcp__plugin_agent-task_agent-task__list_day_log
---

# Progress report

Read `agent-task-workflow` and `agent-task-reporting`. Scope: **$ARGUMENTS**.
Resolve the timeframe and project/space, defaulting to the last seven days.
Use the bundled `agent-task:reporter` when available and delegation is authorized;
otherwise follow the reporting skill directly with read tools only.

Do not mutate tasks, claims, notes, or comments. Do not infer completion dates
from `updatedAt`. Report current blockers separately from changes in the window.
Return the report in the conversation; persistence is a separate user request.
