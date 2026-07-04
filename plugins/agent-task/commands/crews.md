---
description: Sync your space's crews into real Claude Code subagents (+ skills), push local edits back, or sweep for crew @mentions.
argument-hint: sync [space] | push <crew-file> | check
---

# /crews — crews ⇄ Claude Code

Crews are team-authored AI personas stored in Agent Task. This command **materializes** them as
native Claude Code artifacts (subagents + skills) and keeps the two sides in sync. Read the
`agent-task-workflow` and `agent-task-crew-execution` skills first.

Subcommand + args from the user: **$ARGUMENTS**

## /crews sync [space]

1. Resolve the space (`list_spaces`; default to the current project's usual space). Call
   `list_crews({ spaceUuid })` — it returns FULL personas.
2. For each crew, generate `.claude/agents/<kebab-name>.md` from this EXACT template (deterministic
   output — same crew state must always produce the same file):

   ```markdown
   ---
   name: <kebab-name>
   description: <avatar> <name> — <first line of instructions>. Crew <code> from Agent Task (synced; edit there or /crews push).
   <if advise mode>tools: Read, Grep, Glob</if>
   <if runtimeConfig.model>model: <model></if>
   <if runtimeConfig.effort>effort: <effort></if>
   ---
   <!-- agent-task crew: <uuid> · updatedAt: <updatedAt> — DO NOT EDIT THIS LINE -->

   <instructionsMarkdown>

   ## What you must deliver
   <deliverablesMarkdown>
   ```

   **Advise mode compiles to `tools: Read, Grep, Glob`** — that restriction is harness-enforced,
   which is the whole point. Execute mode omits `tools:` (inherits) and, when
   `runtimeConfig.isolation === 'worktree'`, add a body note to prefer worktree isolation.
3. For each linked skill note (`skills[]`): `fetch` the note and write
   `.claude/skills/<kebab-note-title>/SKILL.md` with frontmatter `name` + `description: <title>
   (crew skill <note code>, synced from Agent Task)` and the note's markdown as the body.
4. **Drift check before overwriting**: if an existing generated file's stamp line has the same
   `uuid` but content differs from what you'd generate, the user edited it locally — do NOT
   clobber; show a diff and offer `/crews push` instead.
5. **Consent tier**: agent/skill files are inert — write them without ceremony and list what was
   written. Anything that ACTS on its own (a cadence loop/schedule, a hook, execute-mode write
   permissions beyond default) must be listed as "wants: …" and installed only on explicit yes.
6. Crews with `runtime: universal` → generate a single `AGENTS.md`-style bundle instead
   (persona + deliverables + skills as plain markdown sections).

## /crews push <crew-file>

Reverse sync: parse the stamped `.claude/agents/<file>`, map body → `instructions` (everything
above "## What you must deliver") and → `deliverables` (below it), frontmatter → `runtimeConfig`,
and call `update_crew({ crewUuid: <from stamp>, ... })`. If the server copy changed since the
stamp's `updatedAt`, STOP and show both versions — never clobber a teammate's edit.

## /crews check

The @mention sweep from `agent-task-crew-execution`: scan recent comments on the active/assigned
tasks for unanswered `@<crew>` mentions and offer to engage each. Also list tasks assigned to a
crew with no crew ack yet.

## Notes

- Sync is per-space and idempotent; deleted crews → offer to remove their stamped files.
- Never write outside `.claude/agents/`, `.claude/skills/`, or the repo's `AGENTS.md`.
- A synced crew can never grant itself more than YOUR session can do.
