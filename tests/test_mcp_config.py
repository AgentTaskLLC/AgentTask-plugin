import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from mcp_config import CLIENTS, DEFAULT_URL, render_config, validate_url


class ConfigTests(unittest.TestCase):
    def parse_server(self, client, content):
        if client == "codex":
            return tomllib.loads(content)["mcp_servers"]["agent-task"]
        key = "servers" if client == "vscode" else "mcpServers"
        return json.loads(content)[key]["agent-task"]

    def test_oauth_is_header_free_in_every_client(self):
        for client in CLIENTS:
            with self.subTest(client=client):
                server = self.parse_server(client, render_config(client))
                self.assertEqual(server["url"], DEFAULT_URL)
                self.assertNotIn("headers", server)
                self.assertNotIn("bearer_token_env_var", server)

    def test_api_keys_use_client_native_references(self):
        for client in CLIENTS:
            with self.subTest(client=client):
                server = self.parse_server(client, render_config(client, "api-key"))
                if client == "codex":
                    self.assertEqual(server["bearer_token_env_var"], "AGENT_TASK_API_KEY")
                else:
                    prefix = "" if client == "claude" else "env:"
                    self.assertEqual(server["headers"]["Authorization"],
                                     "Bearer ${" + prefix + "AGENT_TASK_API_KEY}")

    def test_reject_unsafe_or_ambiguous_urls(self):
        for value in (
            "http://example.com/mcp", "ftp://example.com/mcp",
            "https://user:secret@example.com/mcp", "https://example.com/mcp?token=secret",
            "https://example.com/mcp#fragment", "https://example.com/\npath",
            "https://example.com/${SECRET}", "https://example.com:bad/mcp",
            "https:///mcp", "https://example.com\\other/mcp",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_url(value)
        for value in ("http://localhost:8080/mcp", "http://127.0.0.1/mcp", "http://[::1]/mcp"):
            self.assertEqual(validate_url(value), value)

    def test_reject_invalid_environment_identifiers(self):
        for value in ("API-KEY", "${KEY}", "KEY\nOTHER", "1KEY", "key"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render_config("claude", "api-key", key_env=value)

    def test_cli_does_not_read_secret_and_supports_url_override(self):
        env = dict(os.environ, AGENT_TASK_API_KEY="synthetic-test-secret",
                   AGENT_TASK_MCP_URL="https://example.com/mcp")
        command = [sys.executable, str(Path(__file__).resolve().parents[1] / "scripts/mcp_config.py"),
                   "--client", "codex", "--auth", "api-key"]
        result = subprocess.run(command, env=env, text=True, capture_output=True, check=True)
        self.assertNotIn("synthetic-test-secret", result.stdout + result.stderr)
        self.assertEqual(self.parse_server("codex", result.stdout)["url"], "https://example.com/mcp")
