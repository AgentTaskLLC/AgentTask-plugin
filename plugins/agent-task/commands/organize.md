---
description: Reorganize tasks in a chosen scope into a coherent structure — groups, projects, and labels.
argument-hint: [optional: what/where to organize, e.g. "the Marketing project"]
---

# /organize — reorganize work into a clean structure

Bring order to a messy backlog. Propose a structure, get a yes, then re-bucket everything in scope.
Be smart and opinionated about the proposed structure, but **never restructure outside the chosen
scope**, and always confirm before mutating. Read the `agent-task-workflow` skill first.

Hint from the user: **$ARGUMENTS**

## Clarify (skippable, but scope + permission matter)

1. **What + scope** — everything, one space, or one project? If `$ARGUMENTS` is clear, use it;
   otherwise ask. Touch **only** the chosen scope and say so.
2. **Organizing principle** — by theme/area, by status, by priority, or by milestone? Default:
   by theme/area.
3. **Permission** — "May I create new groups, projects, and labels as part of this?" Default: ask
   before creating each new container; never delete anything.

## Plan

- Read all tasks in scope (`list_tasks_and_subtasks`, plus `list_task_groups`, `list_projects`,
  `list_labels`).
- Propose a target structure: which groups/projects should exist (existing + any new ones), a tight
  label taxonomy, and how tasks map onto them. Present it as a clear before → after.
- Wait for confirmation. Let the user amend the plan.

## Execute (after confirmation)

- Create approved new containers (`create_task_group`, `create_project`, `create_label`).
- Re-bucket every task with batched `update_task({ items })`: set `groupUuid`, `projectUuid`, and
  `labels`. Fix obviously-wrong statuses (e.g. a shipped task still in `todo`) — but flag ambiguous
  ones instead of guessing.
- Never delete tasks. Don't move anything outside the chosen scope.

## Report

Show a diff of what moved: counts per group/project, new labels created, tasks relabeled, and any
statuses you corrected. List anything you intentionally left for the user to decide.
