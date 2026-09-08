import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.doc = self.root / "guide.md"

    def test_duplicate_tool_permissions_in_frontmatter_are_rejected(self):
        self.doc.write_text("---\ndescription: Test\ntools: Read\ntools: Bash\n---\n")
        with self.assertRaisesRegex(ValueError, "duplicate YAML key: tools"):
            validate.frontmatter(self.doc)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"url": "trusted", "url": "other"}',
                       object_pairs_hook=validate.no_duplicate_keys)

    def test_markdown_parser_ignores_examples_but_checks_real_links(self):
        self.doc.write_text("# Guide\n\n`[example](missing.md)`\n\n"
                            "```md\n[example](missing.md)\n```\n\n[local](#guide)\n")
        with patch.object(validate, "ROOT", self.root):
            validate.check_links(self.doc)
            self.doc.write_text("[missing](missing.md)")
            with self.assertRaisesRegex(ValueError, "broken local link"):
                validate.check_links(self.doc)

    def command(self, name):
        return Path("plugins/agent-task/commands") / name

    def test_scoped_grants_cannot_smuggle_shell_or_write_past_the_denylist(self):
        # Claude Code writes a narrowed grant as Name(argument). Matching whole entries would let
        # Bash(...) and Write(...) through a ban that only rejects the bare names.
        for value in ("Bash(rm -rf /), mcp__plugin_agent-task_agent-task__fetch",
                      "Write(/etc/passwd), mcp__plugin_agent-task_agent-task__fetch",
                      "WebFetch(domain:evil.example), mcp__plugin_agent-task_agent-task__fetch",
                      "Bash, mcp__plugin_agent-task_agent-task__fetch"):
            with self.assertRaisesRegex(ValueError, "must not preapprove writes or shell"):
                validate.check_allowed_tools(self.command("triage.md"), value)

    def test_read_only_commands_reject_mutating_and_file_writing_tools(self):
        for bare in ("update_task", "add_comment", "start_work", "download_attachments"):
            with self.assertRaisesRegex(ValueError, "must not preapprove"):
                validate.check_allowed_tools(
                    self.command("report.md"), "Task, " + validate.PREFIX + bare)

    def test_read_only_commands_must_keep_delegation_and_name_their_tools(self):
        with self.assertRaisesRegex(ValueError, "must allow Task"):
            validate.check_allowed_tools(
                self.command("standup.md"), validate.PREFIX + "list_comments")
        with self.assertRaisesRegex(ValueError, "must name the MCP tools"):
            validate.check_allowed_tools(self.command("triage.md"), "Read, Grep, Glob")
        validate.check_allowed_tools(
            self.command("report.md"), "Task, " + validate.PREFIX + "list_comments")

    def test_wildcards_and_foreign_mcp_servers_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "must not use a wildcard"):
            validate.check_allowed_tools(self.command("triage.md"), validate.PREFIX + "*")
        with self.assertRaisesRegex(ValueError, "only agent-task MCP tools"):
            validate.check_allowed_tools(
                self.command("triage.md"), "mcp__other_server__do_thing")

    def test_missing_heading_and_escape_are_rejected(self):
        with patch.object(validate, "ROOT", self.root):
            self.doc.write_text("# Guide\n\n[missing](#missing)\n")
            with self.assertRaisesRegex(ValueError, "missing heading"):
                validate.check_links(self.doc)
            self.doc.write_text("[escape](../outside.md)")
            with self.assertRaisesRegex(ValueError, "broken local link"):
                validate.check_links(self.doc)
