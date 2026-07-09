---
name: agent-task-crew-execution
description: Work a task AS its assigned crew (AI persona) — adopt the persona via a sub-agent, acknowledge on engage, deliver the ✅/❌ checklist, and post comments attributed to the crew. Use whenever a fetched task carries crewContext, when the user asks for "the crew's take", or when a crew's involvement trigger matches what you're about to do (e.g. before pushing).
---

# Agent Task — crew engagement

A **crew** is a team-authored AI persona attached to a task (`crewContext` on `fetch`). You are the
orchestrator; the crew is a script you cast a **sub-agent** to play. Read `agent-task-workflow`
for tool conventions first.

## When to engage (explicit-first)

Engage a crew when — in priority order:

1. The **user asks** ("get the QA crew's take", "run the crew").
2. You `/start` or fetch a task and its `crewContext.involvementTrigger` matches the moment:
   - `before_upstream_push` — engage after the diff is final, **before** `git push`.
   - `on_task_complete` — engage before flipping the ticket toward done.
   - `every_comment` — when handling a comment-triggered request on the task.
   - `on_request` — only paths 1 and 3; never ambient.
   - `custom` — follow `involvementNotesMarkdown` literally.
3. A **@mention sweep** (see below) surfaces an unanswered mention of the crew.

Never engage the same crew twice for the same moment (check the task's recent comments for the
crew's ack/result first — its comments are attributed to the crew, or carry its signature line).

## The engagement loop

1. **Acknowledge FIRST** (immediate feedback): before the actual work,
   `add_comment({ targetType, targetId, content: "<avatar> <Crew name> is on it — <one line of what it will check>", crewUuid })`.
2. **Cast the persona sub-agent** via the Agent tool. Build its prompt as:
   - system-of-the-brief: `instructionsMarkdown` verbatim, then
   - "## What you must deliver" + `deliverablesMarkdown`, then
   - the full markdown body of each linked skill note (`skills[]` → `fetch` each `noteUuid`), then
   - the concrete work (the diff, the task description, the question).
   Respect `runtimeConfig`: pass `model`/`effort` to the Agent tool when set. **Advise mode**: tell
   the sub-agent it must not modify files, and do not grant it write tools if you can choose the
   agent type (a synced `.claude/agents/<crew>.md` enforces this structurally — prefer it when it
   exists). When the crew has tool grants (see below), the synced subagent's `tools:` frontmatter
   is the authority — cast THAT subagent rather than improvising a prompt-only persona.
3. **Deliver the checklist**: post the result as ONE comment attributed to the crew — a ✅/❌ line
   per deliverable item, then the findings. Use `add_comment({ ..., crewUuid })`.
4. **Never flip the ticket yourself** on the crew's behalf — the human assignee stays responsible.
   Advise-mode findings are input to the human, not gates you enforce.

## Tool grants (AI-P24)

A crew's capability is data on the crew record, not vibes in its prompt:

- **Mode sets the FILE floor.** Advise = read-only files (`Read, Grep, Glob`), always. Execute
  may write files. This never changes with grants.
- **`runtimeConfig.extraTools` adds product tools deliberately** — e.g. `update_task` (move the
  board), `notify` (ping humans). An advise crew with `extraTools: [update_task]` may change
  TASKS while still unable to touch FILES; that is intended, not a bug.
- **`blockedTools` always wins** — over extras and over the floor.
- `/crews sync` compiles the effective list into the subagent's `tools:` frontmatter; the
  Claude Code harness enforces it mechanically. Grants are additive-only via frontmatter — a
  prompt can never widen them.

**When a needed tool is not granted: STOP.** Report the missing grant in the crew's deliverable
output ("❌ could not update the task — this crew has no `update_task` grant; add it in the crew's
Tools settings") and let the human decide. Never impersonate the crew with your own broader
session, shell around the block, or quietly do it un-attributed. A grant error is the feature
working.

`notify` etiquette: crews send notifications for moments a human must see NOW (blocker, verdict,
handback). Routine progress belongs in `add_comment` — the inbox is not a log file.

## Attribution

Always pass `crewUuid` on crew comments — the board renders the crew avatar + an AI badge +
"via <you>", and the real actor stays recorded. If the server rejects `crewUuid` (older backend),
fall back to prefixing the body with `**<avatar> <Crew name>:** ` on the first line.

## @mention sweep (/crews check)

On session start for a ticket-driven session (or when asked): `list_comments` on the active task(s)
and look for `@<crew name>` mentions newer than the crew's last attributed comment. Offer to engage
for each hit. Crews respond **when engaged** — there is no server-side scheduler; say so if a user
expects real-time replies.

## Standing crews (cadence)

A crew whose `runtimeConfig.cadence` is `loop`/`daily` is a *standing* crew. You may OFFER to start
a `/loop` or a scheduled task running its cadence prompt — with the user's explicit consent, never
automatically. It runs in the user's Claude Code while their machine is up; be honest about that.
