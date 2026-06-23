---
description: Triage the Inbox / unsorted tasks — route each to a group + project, label, set priority, and flag duplicates.
argument-hint: [optional: scope, e.g. "Inbox", a space, or a project]
---

# /triage — process unsorted tasks

Clear the intake pile. Walk the **untriaged** tasks and give each one a home: a group, a project
(if it belongs to one), fitting labels, and a sensible priority — flagging likely duplicates as you
go. Be autonomous; propose a batch and confirm once rather than asking per task. Read the
`agent-task-workflow` skill first.

Scope hint from the user: **$ARGUMENTS**

## Steps

1. **Resolve the space.** `list_spaces`; if there's exactly one, use it, else use what `$ARGUMENTS`
   implies or ask once.
2. **Find the untriaged tasks.** `list_tasks_and_subtasks({ spaceUuid })` (page through the cursor).
   Treat as untriaged anything sitting in the **default / Inbox group**, or with **no project**, **no
   labels**, or **no priority** — i.e. tasks that were quick-captured and never sorted. Narrow to
   `$ARGUMENTS` if it named a group/project.
3. **Propose a routing for each** (don't mutate yet):
   - **Group** — `suggest_group({ spaceUuid, title, description })`; trust an `auto` recommendation,
     otherwise pick from `list_task_groups` using each group's `description` as a hint.
   - **Project** — map to one from `list_projects` when it clearly fits; else leave unlinked.
   - **Labels** — `list_labels`; apply fitting ones, `create_label` only for a clearly-useful
     missing one (keep the taxonomy tight).
   - **Priority** — infer `low|medium|high|urgent` from the content; default `medium`.
   - **Duplicate?** — `search` the title; if it strongly matches an existing task, **flag it** for
     the user (don't merge or delete).
4. **Confirm once.** Show the proposed routing as a compact table (task → group / project / labels /
   priority, plus any duplicate flags). Let the user amend.
5. **Apply.** One batched `update_task({ items: [...] })` setting `groupUuid`, `projectUuid`,
   `labels`, and `priority` for every confirmed task. Don't change status here, and never delete.

## Report

Summarize: how many tasks triaged, the group/project distribution, any new labels created, and a
short list of suspected duplicates left for the user to decide on.
