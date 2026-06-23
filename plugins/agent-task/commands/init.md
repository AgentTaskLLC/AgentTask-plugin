---
description: Stand up a new project via clarifying questions — type, milestones, health, priority, and optional seed groups and tasks.
argument-hint: [project name or idea]
---

# /init — initialize a new project

Create a well-formed project in Agent Task by asking a short series of clarifying questions. **Every
question is skippable** — if the user skips, use a sensible default and say what you assumed. Read
the `agent-task-workflow` skill first.

Project idea from the user: **$ARGUMENTS**

## Clarify (all skippable)

Ask these one at a time or as a short batch; accept "skip" for any:

1. **Space** — which space (only ask if more than one). 
2. **Name** — confirm/derive from `$ARGUMENTS`.
3. **Type** — `initiative` (default), `program`, `epic`, or `operations`.
4. **Dates / milestones** — start date, target date, and any named milestones to track.
5. **Priority** — `none` / `low` / `medium` / `high` / `urgent` (default `medium`).
6. **Health** — `unknown` (default), `on_track`, `at_risk`, `off_track`.
7. **Seed groups?** — offer to create a few workflow groups (e.g. by phase/area), each with a short
   `description` for routing. Skippable.
8. **Seed tasks?** — offer to create a handful of starter tasks. Skippable.

## Execute

- `create_project` with the chosen attributes. Put milestones in the description if there's no
  structured field for them.
- If groups were requested, `create_task_group` for each (with descriptions).
- If starter tasks were requested, `create_task` (batch via `items[]`) — each with a real
  description and fitting labels, mapped to the new project (`update_task({ projectUuid })`) and the
  right group.
- **Scaffold agent guidance** — write a `CLAUDE.md` in the current working directory (the user's
  project root) containing the *Keep tickets updated* block below, so any agent working in this repo
  keeps its Agent Task ticket a live record. If `CLAUDE.md` already exists, **append** the block only
  when that section isn't already present — never overwrite or duplicate existing content. Tell the
  user the file was created/updated (skippable).

## Keep-tickets-updated block to write

When scaffolding, write exactly this section into the project's `CLAUDE.md`:

```markdown
## Agent Task — keep tickets updated

When you work on an Agent Task ticket (e.g. an `AI-…` code) in this repo, keep the ticket a live
record via the Agent Task MCP tools (`add_comment`, `update_task`):

- As you make progress, post short `add_comment` updates at meaningful checkpoints (a sub-goal done,
  a blocker hit/cleared, a decision made) — 1–3 lines: what changed, what's next.
- When you open a PR for the ticket, record it immediately: `update_task({ taskId, prUrl })`, and
  mention it in a comment. Keep `prUrl` current if the PR is replaced.
- When the work is done, leave a final comment summarizing the latest changes and link the merged
  PR. Don't set `status: done` silently — confirm with the user (and that the PR is merged) first.
```

## Report

Give the project code + URL, its type/priority/health/dates, and a list of any groups and starter
tasks created. Note every default you applied where the user skipped.
