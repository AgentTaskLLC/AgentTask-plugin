---
description: Sync your space's crews into real Claude Code subagents (+ skills), sync-and-run a project roster, push local edits back, recommend installed skills/commands, sweep for crew @mentions, or install git hooks for crew triggers.
argument-hint: sync [space] [project] | sync-execute [project] | loop [crew] | push <crew-file> | recommend [crew] | check | hook <install|uninstall|status> [--blocking] [--force]
---

# /crews — crews ⇄ Claude Code

Crews are team-authored AI personas stored in Agent Task. This command **materializes** them as
native Claude Code artifacts (subagents + skills) and keeps the two sides in sync. Read the
`agent-task-workflow` and `agent-task-crew-execution` skills first.

Subcommand + args from the user: **$ARGUMENTS**

## /crews sync [space] [project]

1. Resolve the space (`list_spaces`; default to the current project's usual space). Then resolve
   the scope:
   - If a project is specified (or inferred from the current ticket's project), call
     `list_project_crews({ projectUuid })` (AI-1219) to get crews from the project's roster.
   - Otherwise, fall back to `list_crews({ spaceUuid })` for space-level crews.
2. For each crew, generate `.claude/agents/<kebab-name>.md` from this EXACT template (deterministic
   output — same crew state must always produce the same file):

   ```markdown
   ---
   name: <kebab-name>
   description: <avatar> <name> — <first line of instructions>. Crew <code> from Agent Task (synced; edit there or /crews push).
   <tools: line per the "Tool grants" rules below — omit ONLY for execute mode with no extraTools>
   <if runtimeConfig.skills is non-empty>skills: <comma-joined skill/command names, slash stripped></if>
   <if runtimeConfig.model>model: <model></if>
   <if runtimeConfig.effort>effort: <effort></if>
   ---
   <!-- agent-task crew: <uuid> · updatedAt: <updatedAt> — DO NOT EDIT THIS LINE -->

   <instructionsMarkdown>

   ## What you must deliver
   <deliverablesMarkdown>
   ```

   **Tool grants (AI-P24, docs/crew-tool-grants_8405).** The `tools:` line is computed — never
   copied — from the crew's mode and `runtimeConfig.extraTools`/`blockedTools`:

   ```
   floor(advise)  = [Read, Grep, Glob]            — this exact order, never re-sorted
   floor(execute) = INHERIT (omit the tools: line) when extraTools is empty; [] otherwise
   namespace(t)   = t unchanged when it starts with an uppercase letter (native: Read, Bash)
                  = <detected-prefix> + t otherwise (product tools: update_task, notify, …)
   extras         = sort(unique(namespace(extraTools)) ∖ floor)
   effective      = (floor ∖ namespace(blockedTools)) ++ (extras ∖ namespace(blockedTools))
   emit           = "tools: " + join(", ", effective)
   ```

   Floor order is preserved and extras are appended sorted — so a grant-less advise crew emits
   `tools: Read, Grep, Glob`, byte-identical to the pre-grant template (INV-B2).

   `blockedTools` ALWAYS wins — over `extraTools` and over the floor (a blocked `Grep` is removed
   even in advise mode). **Prefix detection:** look at your own session's agent-task tool names
   (e.g. `mcp__agent-task__update_task` or `mcp__plugin_agent-task_agent-task__update_task`) and
   use that exact prefix; never hardcode one. Unknown short names compile verbatim (the harness
   simply won't match them); `/crews check` may warn, sync never fails on them. Grants must appear
   ONLY in the frontmatter — never restate them as prose in the body (a body line like "you may
   also use X" invites the model to assume un-granted tools).

   Worked examples (prefix `mcp__agent-task__` detected):

   | mode | extraTools | blockedTools | emitted line |
   |---|---|---|---|
   | advise | — | — | `tools: Read, Grep, Glob` |
   | advise | `[update_task, notify]` | — | `tools: Read, Grep, Glob, mcp__agent-task__notify, mcp__agent-task__update_task` |
   | advise | — | `[Grep]` | `tools: Read, Glob` |
   | execute | `[notify]` | — | `tools: mcp__agent-task__notify` ⚠ listing ANY tool replaces inherit-all — warn the user and confirm before writing, or have them add the tools the crew needs |
   | execute | — | — | (no tools: line — inherits everything, byte-identical to pre-grant output) |

   A crew with no grants must compile **byte-identically** to the pre-grant template (drift-check
   safety). When `runtimeConfig.isolation === 'worktree'`, still add the body note to prefer
   worktree isolation.
3. For each linked skill note (`skills[]`): `fetch` the note and write
   `.claude/skills/<kebab-note-title>/SKILL.md` with frontmatter `name` + `description: <title>
   (crew skill <note code>, synced from Agent Task)` and the note's markdown as the body.
3b. **Skills & commands (AI-P24, `runtimeConfig.skills`).** This is a list of EXISTING Claude Code
   skills / slash-commands the crew should use (e.g. `code-review`) — distinct from the linked
   skill NOTES above, which the crew authors. Emit them as the `skills:` frontmatter line (names
   only, any leading slash stripped). Do NOT scaffold files for these — they already exist in the
   environment. If a named skill/command is NOT present in this session (not in `.claude/skills/`,
   `.claude/commands/`, or an installed plugin), still emit it but WARN the user it wasn't found
   here.
4. **Drift check before overwriting**: if an existing generated file's stamp line has the same
   `uuid` but content differs from what you'd generate, the user edited it locally — do NOT
   clobber; show a diff and offer `/crews push` instead.
5. **Cadence auto-configuration (AI-1219)**: If a crew has `runtimeConfig.cadence.mode !== 'on_demand'`:
   - `mode: 'loop'` with `every` (e.g., "15m", "1h") → map to `/loop` command with the interval.
   - `mode: 'daily'` with `at` (HH:MM) → configure a scheduled task using CronCreate with the daily pattern.
   - List this in the "wants: …" consent tier and only configure on explicit user approval.
   - The cadence prompt is stored in `runtimeConfig.cadence.prompt`.

6. **Consent tier**: agent/skill files are inert — write them without ceremony and list what was
   written. Anything that ACTS on its own (a cadence loop/schedule, a hook, execute-mode write
   permissions beyond default) must be listed as "wants: …" and installed only on explicit yes.
   Tool grants beyond the advise floor (any `extraTools`) belong in that "wants: …" list too —
   name each granted tool so the user consents to the crew's real capability.
6. Crews with `runtime: universal` → generate a single `AGENTS.md`-style bundle instead
   (persona + deliverables + skills as plain markdown sections). Render grants as an
   "Allowed tools" section listing the SHORT names, with the note *"documented, not enforced —
   only the Claude Code runtime enforces grants structurally"*.

## /crews push <crew-file>

Reverse sync: parse the stamped `.claude/agents/<file>`, map body → `instructions` (everything
above "## What you must deliver") and → `deliverables` (below it), frontmatter → `runtimeConfig`,
and call `update_crew({ crewUuid: <from stamp>, ... })`. If the server copy changed since the
stamp's `updatedAt`, STOP and show both versions — never clobber a teammate's edit.

**Tools line inversion:** recompute `floor(mode)`, strip your detected prefix from each entry of
the local `tools:` list, then `extraTools = shortname(effective ∖ floor)` and
`blockedTools = shortname(floor ∖ effective)` — pass both to `update_crew` (empty array clears).
sync → push → sync on an unmodified file must be a no-op (fixpoint). Example: advise file with
`tools: Read, Glob, mcp__agent-task__notify` → `extraTools: ["notify"]`, `blockedTools: ["Grep"]`.

**Skills line inversion:** map the `skills:` frontmatter list → `runtimeConfig.skills` (names only)
on the same `update_crew` call.

## /crews recommend [crew]

You are running INSIDE Claude Code, so you can see what capabilities exist here. List the session's
available skills (`.claude/skills/`, plugin skills) and slash-commands (`.claude/commands/`, plugin
commands — e.g. `code-review`), then offer to attach relevant ones to a crew via
`update_crew({ crewUuid, runtimeConfig: { skills: [...] } })`. This is the recommend/set flow the
server can't do on its own — only the harness knows what's installed. Never attach without the
user's explicit pick.

`update_crew`'s `runtimeConfig` is MERGED, so passing only `{ skills: [...] }` updates the Skills &
commands list and leaves the crew's tool grants / model / cadence untouched. To clear the list pass
`{ skills: [] }`.

## /crews check

The @mention sweep from `agent-task-crew-execution`: scan recent comments on the active/assigned
tasks for unanswered `@<crew>` mentions and offer to engage each. Also list tasks assigned to a
crew with no crew ack yet.

## /crews sync-execute [project]

Sync a **project's crew roster** into subagents (as `/crews sync <space> <project>` does), then
immediately **engage** each rostered crew on the project's active work — a one-shot "materialize
and run" for project-level automation (AI-1224). Crews are project-level (AI-P38): the roster is
the automation context for every task in the project.

1. Resolve the project (explicit arg, or inferred from the current ticket's project). Call
   `list_project_crews({ projectUuid })` to get the roster in order (the **first** crew is the
   project default).
2. Run the normal `sync` materialization for those crews (agents + skills + consent tier). Anything
   that ACTS on its own still requires explicit approval — see the consent tier in `sync`.
3. For each rostered crew, engage it per `agent-task-crew-execution`: adopt the persona in a
   sub-agent, work the project's in-scope tasks (respecting each crew's `executionMode` — advise vs
   execute), and post crew-attributed comments. Process crews in roster order; the default crew
   leads unless the user picks another.
4. Summarize what each crew did (✅/❌ against its deliverables) and stop — `sync-execute` is a
   single pass, not a standing loop. For recurring runs use a crew cadence + `/crews loop`.

**Scope guard:** `sync-execute` only touches the resolved project's tasks. It never engages crews
outside the roster, and execute-mode file changes still follow your session's own permissions.

## /crews loop [crew]

Materialize a **standing crew's cadence** (`runtimeConfig.cadence`) as a recurring runner (AI-1208).
A synced crew never auto-starts its own loop — this command is the explicit, consented step.

1. Resolve the crew (arg, or pick from the space's crews with a non-`on_demand` cadence).
2. Read `runtimeConfig.cadence`:
   - **`mode: 'loop'`** (`every: "15m" | "1h"`, `prompt`) → run the `/loop` skill at that interval
     with the cadence `prompt` as the task, e.g. `/loop 15m <prompt>`.
   - **`mode: 'daily'`** (`at: "HH:MM"`, `prompt`) → create a scheduled task (the `schedule` skill /
     `CronCreate`) that runs the `prompt` daily at that time.
   - **`tz`** (optional IANA zone, e.g. `America/New_York`) → anchor `daily.at` (and any wall-clock
     interpretation of `loop`) to that zone; otherwise use local time.
   - **`mode: 'on_demand'`** → nothing to loop; tell the user the crew is on-demand.
3. This ACTS on its own, so it belongs in the "wants: …" consent tier — start it only on explicit
   approval, and remind the user they can stop it anytime (end the `/loop`, or delete the schedule).

## Auto-check on trigger match (AI-1210)

When an event matches a crew's `involvementTrigger`, proactively offer `/crews check` for the crews
whose trigger fired — don't wait to be asked:
- **`before_upstream_push`** — the pre-push hook (see `/crews hook`) reminds you before a push; run
  `/crews check` (or `/crews sync-execute <project>`) for those crews first.
- **`every_comment`** — after new comments land on an active task, sweep for `@<crew>` mentions and
  unanswered crew asks.
- **`on_task_complete`** — when you mark a task done, offer the completion-trigger crews a look.
Auto-check only *surfaces* the match; engaging a crew still follows its `executionMode` and your
session's permissions.

## Status line (AI-1209)

A status-line script ships with the plugin and shows how many crews are synced into this repo and
how many are **standing** (have a loop/daily cadence). Wire it into Claude Code `settings.json`:

```json
{ "statusLine": { "type": "command",
    "command": "bash \"${CLAUDE_PLUGIN_ROOT}/statusline/crew-statusline.sh\"" } }
```

It scans `.claude/agents/` for `/crews sync`-stamped crew files and prints e.g. `🤖 crews: 3 (2 standing)`
(empty when the repo has no synced crews).

## /crews hook <install|uninstall|status> [--blocking] [--no-backup] [--force]

Manage the pre-push git hook for the `before_upstream_push` crew trigger (AI-1207). The hook and a
deterministic installer ship with the plugin — run the installer rather than hand-writing hooks:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/hooks/install-crew-hooks.sh" install [--blocking] [--no-backup] [--force]
bash "${CLAUDE_PLUGIN_ROOT}/hooks/install-crew-hooks.sh" uninstall
bash "${CLAUDE_PLUGIN_ROOT}/hooks/install-crew-hooks.sh" status
```

(`${CLAUDE_PLUGIN_ROOT}` is the installed plugin path; if unset, use this plugin's directory.)

**Options:**
- `--blocking` — install in blocking mode (default: non-blocking)
- `--no-backup` — skip backing up an existing foreign pre-push hook (used with `--force`)
- `--force` — overwrite an existing non-Agent-Task pre-push hook

**Honest behavior (important):** a git hook runs in a plain shell and *cannot* drive an interactive
Claude Code session, so it does **not** silently run crews. Instead it **reminds/gates**:
1. On `git push`, the hook prints a reminder to engage `before_upstream_push` crews in Claude Code
   (`/crews check`, or `/crews sync-execute <project>`).
2. **Non-blocking (default):** prints the reminder and allows the push.
3. **Blocking:** aborts the push unless you acknowledge with `AGENT_TASK_HOOK_ACK=1 git push …`
   (after running the crews), or bypass with `git push --no-verify`.

The installer only ever replaces a hook carrying the Agent Task marker (`agent-task-crew-hook`);
a foreign hook is refused unless you pass `--force`, and `uninstall`/`status` key off the same marker.

**Runtime env:** `AGENT_TASK_HOOK_BLOCKING=true` (force blocking for one push),
`AGENT_TASK_HOOK_ACK=1` (acknowledge, allows a blocking push), `AGENT_TASK_HOOK_SILENT=true`
(suppress output).

## Notes

- Sync is per-space/project and idempotent; deleted crews → offer to remove their stamped files.
- Never write outside `.claude/agents/`, `.claude/skills/`, or the repo's `AGENTS.md`.
- A synced crew can never grant itself more than YOUR session can do.

## Crews are project-level (AI-P38)

- Task-level crew assignment has been **removed** — there is no `crew_id` on a task. Crews are
  assigned on the **project crew roster** (`list_project_crews`), which is the automation context
  for every task in the project. The first crew in roster order is the project **default**.
- When syncing/executing for a project, use its roster; when no project is in scope, `list_crews`
  gives the space's whole crew library.
- A fetched task's `crewContext` (via MCP `fetch`) is derived from its project's default roster
  crew — that is how an agent adopts the right persona for a task.
- `/crews push` updates the crew definition itself (persona/skills), independent of any roster.
