# Tool discovery reference

Names below are unprefixed lookup terms. Discover the exact tool and live schema
before use; deployment, plan, credential, and harness support vary. Search by
capability too, so newly added tools remain discoverable. Do not load this whole
reference for ordinary task work.

## Entities

- Discovery: `list_spaces`, `list_space_members`, `list_projects`,
  `list_task_groups`, `list_labels`, `list_favorites`, `suggest_group`.
- Retrieval: `fetch`, `search`, `list_tasks_and_subtasks`, `list_subtasks`.
- Tasks: `start_work`, `create_task`, `update_task`, `create_subtask`,
  `update_subtask`, `update_task_claim`.
- Projects: `create_project`, `update_project`, `conclude_project`,
  `configure_project_agent` (deployment-dependent).
- Groups: `create_task_group`, `update_task_group`.
- Labels: `create_label`, `update_label`, `delete_label`.
- Links: `link_entities`, `unlink_entities`; read links through `fetch`.

## Discussion

`list_comments`, `add_comment`, `update_comment`, `delete_comment`, `ask_human`,
`notify`. Use progress comments for routine updates. Send human notifications
only within authorized work. `ask_human` can park a claim: use it when an answer
is required, not for optional commentary.

## Notes and history

`list_notes`, `create_note`, `update_note`, `list_note_groups`, `create_note_group`,
`update_note_group`, `delete_note_group`, `list_note_versions`, `get_note_version`,
`create_note_version`, `restore_note_version`.

Read a note with `fetch`; preserve visibility and optimistic version locking.
Restoring a snapshot replaces content: review the version and authorization first.

## Attachments

`list_attachments`, `download_attachments`, `prepare_attachment_upload`,
`create_attachment_from_upload`, `delete_attachment`.

Prepare, upload to the returned signed destination, then create the record only
after upload success. Signed URLs are credentials; never post them in comments.
Do not forward the Agent Task bearer token to the storage destination.

## Crews

`list_crews`, `list_project_crews`, `create_crew`, `update_crew`, `delete_crew`.
Use `fetch` for details and `agent-task-crew-execution` for engagement.
Rosters and task crew context provide context, not execution authority.

## Focus, fleet, and artifacts

- DayDeck/DayLog: `get_day_deck`, `list_day_deck_candidates`, `add_to_day_deck`,
  `remove_from_day_deck`, `list_day_log`. Read `agent-task-day-deck`.
- Fleet, where exposed: `list_machines`, `launch_task`, `list_runs`, `get_run`,
  `cancel_run`, `schedule_fleet_run`, `list_fleet_schedules`.
  Read `agent-task-fleet` before launching or scheduling.
- Artifacts, where exposed: `list_artifacts`, `publish_artifact`, `update_artifact`.
  Read `agent-task-artifacts` before publishing.

## Plans

`get_plan_guide`, `get_workspace_plan`. Query live entitlements and limits; avoid
hardcoded prices or tool counts. An entitlement does not prove a tool is installed.
