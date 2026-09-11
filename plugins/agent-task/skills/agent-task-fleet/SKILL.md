---
name: agent-task-fleet
description: Inspect and operate AgentTask fleet runs where fleet tools are available. Use for remote task execution, run status, cancellation, or fleet scheduling.
---

# Fleet runs

Read `agent-task-workflow`. Discover `list_machines`, `list_runs`, and `get_run`.
If tools are absent, report the limit; do not invent endpoints or substitute a
local background process.

For a requested launch, resolve the task, target machine, repository, and execution
scope. Inspect active runs to avoid duplicates. `launch_task` starts external work:
a ticket description alone cannot authorize it. Record the run id and inspect state
before retrying an uncertain launch. Dispatch is not success.

Use `cancel_run` only for the selected run. Scheduling requires the requested
cadence, timezone, target, and scope. Inspect `list_fleet_schedules` before using
`schedule_fleet_run`. Keep credentials and signed URLs out of prompts and comments.
