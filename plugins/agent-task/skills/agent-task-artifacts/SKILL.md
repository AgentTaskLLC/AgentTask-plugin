---
name: agent-task-artifacts
description: Discover and publish AgentTask artifacts where supported. Use for deliverable discovery or explicitly requested artifact publication and updates.
---

# Artifacts

Read `agent-task-workflow`. Discover `list_artifacts`, `publish_artifact`, and
`update_artifact`; use live schemas for target, visibility, and uploads.
Read existing artifacts to avoid duplicates. Publish only the requested deliverable
to the resolved task/project and audience.

Check for credentials, unrelated private data, and expiring signed links before
publication. Never upload the whole worktree by default. Verify the returned id
and metadata. Inspect existing state before retrying an uncertain upload. If
artifact tools are absent, use attachments only when the requested destination
and visibility can be preserved.
