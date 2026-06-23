---
name: agent-task-workflow
description: Foundation for driving Agent Task over its MCP server — the lookup order (spaces → groups → members → labels), how to resolve an AI-XX code to the UUID the tools require, and the canonical enum sets. Read this before using the /start, /update, /report, /organize, /init, or /finish commands, or any time you operate on Agent Task tasks, projects, groups, labels, or notes.
---

# Agent Task — foundation workflow

Shared conventions for every Agent Task command. The commands orchestrate the MCP **tools**;
this skill is the knowledge they assume.

## Golden rule: address things by UUID

The tools take **UUIDs** (`spaceUuid`, `taskId`/`subtaskId` as UUIDs, `groupUuid`,
`projectUuid`, label UUIDs) — never the human-facing `AI-XX` code or a raw numeric id. The one
exception is the **assignee**, which is a numeric **user id** (or `"me"` / a username / an email).

## Standard lookup order

```
list_spaces                 → pick the space, keep its uuid (or slug)
list_task_groups(space)     → pick the group               (only if you need a non-default group)
suggest_group(space,title)  → let the board suggest a group (optional, read-only routing aid)
list_projects(space)        → pick the project             (only if you map to a project)
list_space_members(space)   → resolve an assignee → userId (only if you assign)
list_labels(space)          → resolve / create labels      (only if you label)
<action>                    → start_work / create_task / update_task / create_subtask / add_comment …
```

Run the middle steps only when the action needs them.

## Resolving an `AI-XX` code

`AI-45` is a display code, **not** an identifier you can pass — `fetch` and the space-scoped tools
reject it (`invalid input syntax for type uuid`). To act on it: `search({ query: "AI-45" })` (or
`list_tasks_and_subtasks({ spaceUuid })`), find the task whose `code` is `AI-45`, and use its
**`uuid`**. (`fetch` *does* accept the task's app URL or UUID.)

## The consolidated tool set

| Goal | Tool |
|------|------|
| Discover | `list_spaces`, `list_task_groups`, `list_projects`, `list_space_members`, `list_labels` |
| Find | `search` (tasks/notes org-wide, projects need a space), `list_tasks_and_subtasks` (filter by space/status/assignee/project/group), `list_subtasks` (one task's children), `list_comments`, `fetch` (any entity by UUID/URL) |
| Begin work | `start_work` (resumes/claims your ticket, else creates one) |
| Create | `create_task` (batch via `items[]`), `create_subtask`, `create_project`, `create_task_group`, `create_label`, `create_note` |
| Update | `update_task`, `update_subtask`, `update_project`, `update_task_group`, `update_note`, `update_label` — each takes **any subset** of fields in one call |
| Comment | `add_comment`, `update_comment`, `delete_comment` |
| Attach | `list_attachments`, `download_attachments`, `prepare_attachment_upload` → `create_attachment_from_upload`, `delete_attachment` |
| Route | `suggest_group` (ranked group suggestion + confidence, read-only) |

`update_task` and `update_subtask` are polymorphic — pass only the fields you want to change
(status, priority, title, description, assignee, **labels**, group, project, dueDate, **prUrl**,
isBlocked). Labels are a **replace set**: `[]` clears them. Labels work on **subtasks** too.

`start_work` returns `action`: `resumed` | `picked_up` | `created`. If it resumed or picked up a
ticket, **continue that one — don't create a duplicate**. Pass `title` only to force a new ticket.

## Enum cheat-sheet

- **task / subtask status:** `backlog`, `todo`, `in_progress`, `done`, `canceled`, `duplicate`
- **task priority:** `low`, `medium`, `high`, `urgent`
- **project status:** `backlog`, `planned`, `active`, `paused`, `completed`, `archived`
- **project priority:** `none`, `low`, `medium`, `high`, `urgent`
- **project health:** `unknown`, `on_track`, `at_risk`, `off_track`
- **project type:** `initiative`, `program`, `epic`, `operations`

## Gotchas

- **Comments & attachments need the *space's* `spaceUuid`** — plus the task/subtask `targetId`.
  Passing the task's UUID as `spaceUuid` fails with `space_not_found`. Get the space UUID from
  `list_spaces` (or infer it from the task), then pass `targetId` = the task/subtask UUID.
- A space-scoped tool returns `not_found` if the UUID belongs to another org/space — that's tenant
  isolation, not a bug. Re-resolve from `list_spaces`.
- `create_task` doesn't set a project; create, then `update_task({ projectUuid })`.
- Prefer one batched `update_task({ items: [...] })` over many single calls when touching many tasks.
- `search` and `list_tasks_and_subtasks` are **cursor-paginated** (`nextCursor` / `cursor`); page
  through when you need the full set. Omitting `spaceUuid` searches across all your authorized spaces.
- `spaceUuid` accepts a **slug** as well as a UUID. Most space-scoped read tools (`list_subtasks`,
  `list_comments`, `fetch`) can **infer** the space from the entity, so `spaceUuid` is optional there.
