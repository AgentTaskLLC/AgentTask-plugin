---
description: Start a task properly — map it to a project + group, write a description, apply labels, claim it, and set it in progress.
argument-hint: [task code/title, or describe the work]
---

# /start — begin a task with full context

You are starting work on a task in Agent Task. Be autonomous: infer what you can, ask only what
you genuinely can't determine, and never block on a question that has a sensible default. Read the
`agent-task-workflow` skill for the lookup order, UUID rule, and enums.

Input from the user: **$ARGUMENTS** (may be an `AI-XX` code, a title, a rough description, or empty).

## Steps

1. **Resolve the space.** `list_spaces`. If there's exactly one, use it. If several and the input
   doesn't imply one, ask which space.
2. **Resolve the task.**
   - If the input is an `AI-XX` code or matches an existing task (`search`), use that task.
   - Otherwise treat the input as new work and create it (next step). If the input is empty, fall
     back to `start_work` (it resumes the active ticket or picks up the oldest todo) and skip to 6.
3. **Map to project + group.** Call `suggest_group({ spaceUuid, title, description })` for a ranked
   group suggestion — when its recommendation is `auto`, trust it; when `ask`, fall back to scanning
   `list_task_groups` (use each group's `description` as a routing hint). Pick a project from
   `list_projects`. **Only ask** when it's genuinely ambiguous or nothing fits — and offer to create
   a new project/group if appropriate. The user may skip; default to the space's default group and no
   project.
4. **Write a description.** Draft a concise, useful task description (goal, acceptance, any context
   from the conversation). Don't leave it blank.
5. **Apply labels.** `list_labels`; pick the fitting ones. Create missing labels (`create_label`)
   when a clearly-useful one doesn't exist — keep the taxonomy tight, don't invent noise.
6. **Create / claim.** Create with `create_task` (or reuse the found task), then a single
   `update_task` to set: `status: in_progress`, `assignee: "me"`, `groupUuid`, `projectUuid`,
   `labels`, and the `description`. (For subtasks use `create_subtask` / `update_subtask` — labels
   work there too.) For the empty-input / pick-up path, `start_work` takes a **contention claim** —
   if it returns `already_claimed`, another agent holds it: surface that and pick a different ticket
   rather than working it in parallel (see the **Claiming & contention** section of
   `agent-task-workflow`).
7. **Record this session's context on the claim (AI-898).** So the ticket shows *which live session,
   on which machine, in which repo/branch* is working it, take the claim via `start_work` and pass
   your execution context. Gather it once with a single shell call —
   `pwd; git branch --show-current 2>/dev/null; hostname; uname -sr` — and use your own session id.
   Then call `start_work` (no `title`) with `{ spaceUuid, sessionId, sessionName, worktreePath,
   branch, hostname, os }` — `sessionName` is a short human label for this session (e.g. the ticket
   code + a few words of what you're doing, like "AI-898 claim context"); the id stays the key. It
   resumes the ticket you just set in_progress and stamps the context onto its claim (this
   is the same call that already handles the empty-input / pick-up path). Records only — it never
   changes claim state. Later, when a PR opens, refresh it with
   `update_task_claim({ taskUuid, prUrl })`. Pass only the fields you actually have; omit any you
   can't determine (e.g. `branch` outside a git repo). If `start_work` returns `already_claimed`,
   surface the contention instead of overwriting.
8. **Coding work?** If this task involves code, note that the PR URL should be recorded on the task
   later via `update_task({ prUrl })` (see `/finish` and the periodic update behavior).

## Report

Tell the user, concisely: the task code + title, the project/group it landed in, the labels
applied, and that it's claimed + in progress. List any assumptions you made so they can correct.
