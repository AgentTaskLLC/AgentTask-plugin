---
name: agent-task-branch-link
description: Map between git branches/PRs/commits and Agent Task tickets — derive the active AI-XX ticket from the branch name, name new branches/commits after the ticket, and keep the PR link in sync. Use whenever you work on code that belongs to an Agent Task ticket.
---

# Agent Task — branch ↔ ticket linking

Keep git and the ticket pointing at each other so the right ticket gets updated without re-asking.
Read `agent-task-workflow` for the tool surface and the `AI-XX` → UUID resolution rule.

## Deriving the active ticket from git

When work is already on a branch, infer the ticket instead of asking:

1. Read the current branch (`git branch --show-current`) and look for a ticket **code** —
   typically `AI-<n>` / `WORK-<n>`, e.g. `fix/ai-306-custom-field…` → `AI-306`,
   `feat/AI-57-github-app` → `AI-57` (case-insensitive; the code is usually the first
   `[A-Z]+-\d+` token).
2. Resolve it to a UUID with `search({ query: "AI-306" })` (codes can't be passed to the tools).
3. If the branch carries no code, check recent commit subjects (`git log -n 20 --format=%s`) for a
   `AI-XX` reference before falling back to asking the user.

Use that ticket as the target for progress comments, `prUrl`, and status — see
`agent-task-progress`.

## Naming branches & commits after a ticket

When you start a ticket and then create a branch:

- Branch: `<type>/<code-lowercased>-<short-slug>` — e.g. `fix/ai-306-custom-field-write`,
  `feat/ai-317-feedback-tab`. The embedded code is what makes the link recoverable later.
- Commit subjects / PR titles: reference the code, e.g. `fix(ai-306): …`. This keeps the ticket
  discoverable from `git log` and from the PR.

## Keeping the link current

- When a PR opens, record it on the ticket immediately: `update_task({ taskId, prUrl })`, and
  mention it in a comment. Re-set `prUrl` if the PR is replaced.
- One branch ↔ one ticket. If a branch spans several tickets, pick the primary for `prUrl` and
  comment the others, or split the work.

## When it's ambiguous

If multiple codes appear, or the derived code doesn't resolve (wrong org/space, archived), **ask**
which ticket rather than guessing — acting on the wrong ticket is worse than a quick question.
