---
description: Capture a note (decision, meeting, spec) in a space and link the related tasks.
argument-hint: [the note content or a topic]
---

# /note — capture a note

Persist a decision, meeting summary, spec, or scratch idea as an Agent Task **note**, and link it to
the work it relates to. Be autonomous: draft a clean note from the input/conversation and confirm
only what you can't infer. Read the `agent-task-workflow` skill first.

Input from the user: **$ARGUMENTS** (the note body, a topic, or empty — then use the conversation).

## Steps

1. **Resolve the space.** `list_spaces`; one → use it, else use what `$ARGUMENTS` implies or ask.
2. **Draft the note.** Compose a clear **title** and **content** (markdown) from the input and recent
   conversation — structure it (e.g. *Context / Decision / Next steps* for a decision; *Notes /
   Actions* for a meeting). Don't just dump raw text.
3. **Visibility.** Default `private` (owner only). If it's clearly team-relevant (a decision, shared
   spec), propose `shared` with the space — confirm before sharing.
4. **Link related tasks.** Mention related `AI-XX` codes in the body. For closely-tied tasks, offer
   to drop a one-line `add_comment` on them pointing back to the note.
5. **Create.** `create_note({ spaceUuid, title, content, visibility })`.

## Report

Give the note's title + URL, its visibility, and any tasks you linked or commented on.
