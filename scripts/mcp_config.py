#!/usr/bin/env python3
"""Print client-specific MCP configuration without reading or writing secrets."""

import argparse
import json
import os
import re
from urllib.parse import urlsplit

DEFAULT_URL = "https://app.agent-task.com/v1/public/mcp"
CLIENTS = ("claude", "codex", "cursor", "vscode")


def validate_url(value):
    # Avoid URL parser normalization hiding whitespace or credential-bearing input.
    if any(ord(char) <= 32 or ord(char) == 127 for char in value):
        raise ValueError("MCP URL must not contain whitespace or control characters")
    parsed = urlsplit(value)
    local = parsed.hostname in ("localhost", "127.0.0.1", "::1")
    if parsed.scheme != "https" and not (parsed.scheme == "http" and local):
        raise ValueError("MCP URL requires HTTPS (HTTP is allowed only on loopback)")
    if not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError("MCP URL must have a host and no embedded credentials")
    if parsed.query or parsed.fragment or "$" in value or "\\" in value:
        raise ValueError("MCP URL cannot contain query, fragment, interpolation, or backslash")
    try:
        parsed.port
    except ValueError as error:
        raise ValueError("MCP URL has an invalid port") from error
    return value


def render_config(client, auth="oauth", url=DEFAULT_URL, key_env="AGENT_TASK_API_KEY"):
    if client not in CLIENTS or auth not in ("oauth", "api-key"):
        raise ValueError("unsupported client or authentication mode")
    validate_url(url)
    if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", key_env):
        raise ValueError("key environment variable must be an uppercase identifier")
    if client == "codex":
        lines = ["[mcp_servers.agent-task]", "url = " + json.dumps(url)]
        if auth == "api-key":
            lines.append("bearer_token_env_var = " + json.dumps(key_env))
        return "\n".join(lines) + "\n"

    server = {"url": url}
    if client != "cursor":
        server["type"] = "http"
    if auth == "api-key":
        reference = "${" + ("" if client == "claude" else "env:") + key_env + "}"
        server["headers"] = {"Authorization": "Bearer " + reference}
    root_key = "servers" if client == "vscode" else "mcpServers"
    return json.dumps({root_key: {"agent-task": server}}, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=CLIENTS, required=True)
    parser.add_argument("--auth", choices=("oauth", "api-key"), default="oauth")
    parser.add_argument("--url", default=os.environ.get("AGENT_TASK_MCP_URL", DEFAULT_URL))
    parser.add_argument("--key-env", default="AGENT_TASK_API_KEY")
    args = parser.parse_args()
    try:
        result = render_config(args.client, args.auth, args.url, args.key_env)
    except ValueError as error:
        parser.error(str(error))
    print(result, end="")


if __name__ == "__main__":
    main()
