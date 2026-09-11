import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1] / "plugins/agent-task"
INSTALLER = PLUGIN / "git-hooks/install-crew-hooks.sh"
STATUS = PLUGIN / "statusline/crew-statusline.sh"
SESSION = PLUGIN / "scripts/session-start.sh"
UUID = "01234567-89ab-cdef-0123-456789abcdef"


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "Bash and Git required")
class ShellTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve() / "repo with spaces"
        self.repo.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("GIT_", "AGENT_TASK_", "CLAUDE_"))}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.git("init", "-q", "-b", "main")
        self.hook = self.repo / ".git/hooks/pre-push"

    def run_command(self, command, *, cwd=None, env=None, payload="", check=True):
        result = subprocess.run(command, cwd=cwd or self.repo,
                                env=dict(self.env, **(env or {})), input=payload,
                                text=True, capture_output=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result

    def git(self, *args):
        return self.run_command(["git", *args])

    def install(self, *args, **kwargs):
        return self.run_command(["bash", str(INSTALLER), *args], **kwargs)

    def crew(self, standing=False):
        path = self.repo / ".claude/agents/reviewer.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "daily" if standing else "on_demand"
        path.write_text(f"<!-- agent-task crew: {UUID} -->\n"
                        f"<!-- agent-task cadence: {mode} -->\n", encoding="utf-8")
        return path

    def test_no_crews_means_no_output_or_gate(self):
        self.install("install", "--blocking")
        result = self.run_command(["bash", str(self.hook)])
        self.assertEqual(result.stdout + result.stderr, "")

    def test_silent_mode_preserves_blocking_and_ack_decision(self):
        self.crew()
        self.install("install", "--blocking")
        env = {"AGENT_TASK_HOOK_SILENT": "true"}
        result = self.run_command(["bash", str(self.hook)], env=env, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout + result.stderr, "")
        self.run_command(["bash", str(self.hook)], env=dict(env, AGENT_TASK_HOOK_ACK="1"))
        self.run_command(["bash", str(self.hook)],
                         env=dict(env, AGENT_TASK_HOOK_BLOCKING="false"))

    def test_portable_crews_are_detected_but_metadata_is_not(self):
        directory = self.repo / ".agent-task/crews"
        directory.mkdir(parents=True)
        (directory / (UUID + ".sync.json")).write_text("{}", encoding="utf-8")
        self.install("install", "--blocking")
        self.run_command(["bash", str(self.hook)])
        (directory / (UUID + ".json")).write_text(json.dumps({"uuid": UUID}), encoding="utf-8")
        result = self.run_command(["bash", str(self.hook)], check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("synced crews", result.stderr)

    def test_foreign_hook_requires_force_and_backups_never_collide(self):
        for content in ("#!/bin/sh\nexit 7\n", "#!/bin/sh\nexit 8\n"):
            self.hook.write_text(content, encoding="utf-8")
            refused = self.install("install", check=False)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(self.hook.read_text(encoding="utf-8"), content)
            self.install("install", "--force")
        backups = sorted(path.read_text(encoding="utf-8") for path in self.hook.parent.glob("pre-push.backup.*"))
        self.assertEqual(backups, ["#!/bin/sh\nexit 7\n", "#!/bin/sh\nexit 8\n"])
        self.install("uninstall")
        self.assertFalse(self.hook.exists())
        self.assertEqual(len(list(self.hook.parent.glob("pre-push.backup.*"))), 2)

    def test_uninstall_preserves_foreign_hook(self):
        self.hook.write_text("foreign", encoding="utf-8")
        self.assertNotEqual(self.install("uninstall", check=False).returncode, 0)
        self.assertEqual(self.hook.read_text(encoding="utf-8"), "foreign")

    def test_no_backup_requires_force(self):
        self.assertNotEqual(self.install("install", "--no-backup", check=False).returncode, 0)
        self.hook.write_text("foreign", encoding="utf-8")
        self.install("install", "--force", "--no-backup")
        self.assertEqual(list(self.hook.parent.glob("pre-push.backup.*")), [])

    def test_symlink_hook_and_hooks_directory_are_refused(self):
        outside = self.repo.parent / "outside"
        outside.write_text("keep", encoding="utf-8")
        self.hook.symlink_to(outside)
        self.assertNotEqual(self.install("install", "--force", check=False).returncode, 0)
        self.assertEqual(outside.read_text(encoding="utf-8"), "keep")
        linked = self.repo / "linked-hooks"
        linked.symlink_to(self.hook.parent, target_is_directory=True)
        self.git("config", "core.hooksPath", str(linked))
        self.assertNotEqual(self.install("install", check=False).returncode, 0)

    def test_symlinked_ancestor_directory_still_installs(self):
        link = Path(self.temp.name) / "link to repo"
        link.symlink_to(self.repo, target_is_directory=True)
        self.install("install", cwd=link)
        self.assertTrue(self.hook.is_file())
        self.assertIn("installed by AgentTask", self.install("status", cwd=link).stdout)
        self.install("uninstall", cwd=link)
        self.assertFalse(self.hook.exists())

    def test_symlinked_pre_push_is_refused_by_every_command(self):
        outside = self.repo.parent / "outside hook"
        outside.write_text("keep", encoding="utf-8")
        self.hook.symlink_to(outside)
        for arguments in (["install"], ["install", "--force"], ["uninstall"], ["status"]):
            self.assertNotEqual(self.install(*arguments, check=False).returncode, 0)
        self.assertTrue(self.hook.is_symlink())
        self.assertEqual(outside.read_text(encoding="utf-8"), "keep")

    def test_legacy_marker_hook_is_recognised_as_ours(self):
        legacy = ("#!/usr/bin/env bash\n"
                  "# MARKER: agent-task-crew-hook  "
                  "(do not remove; /crews hook uninstall keys off it)\n")
        self.hook.write_text(legacy, encoding="utf-8")
        self.assertIn("installed by AgentTask", self.install("status").stdout)
        self.install("install")
        self.assertNotEqual(self.hook.read_text(encoding="utf-8"), legacy)
        self.assertEqual(list(self.hook.parent.glob("pre-push.backup.*")), [])
        self.hook.write_text(legacy, encoding="utf-8")
        self.install("uninstall")
        self.assertFalse(self.hook.exists())
        self.hook.write_text("#!/bin/sh\n# docs mention # MARKER: agent-task-crew-hook here\n", encoding="utf-8")
        self.assertNotEqual(self.install("install", check=False).returncode, 0)

    def test_relative_hooks_path_and_read_only_status(self):
        self.git("config", "core.hooksPath", ".custom/hooks")
        self.install("status")
        target = self.repo / ".custom/hooks/pre-push"
        self.assertFalse(target.parent.exists())
        nested = self.repo / "nested"
        nested.mkdir()
        self.install("install", cwd=nested)
        self.assertTrue(target.is_file())
        self.assertFalse(self.hook.exists())

    def test_linked_worktree_uses_shared_hooks(self):
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "commit", "--allow-empty", "-qm", "fixture")
        worktree = self.repo.parent / "linked worktree"
        self.git("worktree", "add", "-qb", "other", str(worktree))
        self.install("install", cwd=worktree)
        self.assertTrue(self.hook.is_file())

    @unittest.skipUnless(shutil.which("jq"), "jq required")
    def test_statusline_uses_payload_workspace_and_explicit_cadence(self):
        self.crew(standing=True)
        payload = json.dumps({"workspace": {"current_dir": str(self.repo)}, "cwd": "/missing"})
        result = self.run_command(["bash", str(STATUS)], cwd=self.repo.parent, payload=payload)
        self.assertEqual(result.stdout, "crews: 1 (1 standing)\n")
        for value in ("not json", "{}", "[]", json.dumps({"cwd": "/missing"})):
            self.assertEqual(self.run_command(["bash", str(STATUS)], payload=value).stdout, "")
        self.assertEqual(self.run_command(["bash", str(STATUS)],
                         payload=json.dumps({"cwd": str(self.repo)})).stdout,
                         "crews: 1 (1 standing)\n")
        nested = self.repo / "nested"
        nested.mkdir()
        self.assertEqual(self.run_command(["bash", str(STATUS)],
                         payload=json.dumps({"workspace": {"current_dir": str(nested)}})).stdout,
                         "crews: 1 (1 standing)\n")

    @unittest.skipUnless(shutil.which("jq"), "jq required")
    def test_session_hook_exposes_only_ticket_hint(self):
        self.git("switch", "-qc", "codex/ai-3126-untrusted-branch-text")
        payload = json.dumps({"cwd": str(self.repo)})
        result = self.run_command(["bash", str(SESSION)], cwd=self.repo.parent, payload=payload)
        self.assertIn("AI-3126", result.stdout)
        self.assertNotIn("untrusted-branch-text", result.stdout)
        for value in ("{}", "not json"):
            self.assertEqual(self.run_command(["bash", str(SESSION)], payload=value).stdout, "")
