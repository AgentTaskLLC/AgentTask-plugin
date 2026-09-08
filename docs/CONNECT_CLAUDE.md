# Connect Claude

The maintained [connection guide](CONNECT.md) covers Claude Code, Codex, Cursor,
VS Code, and generic MCP clients. This page remains as a stable link for existing
installations.

For Claude Code, install the [plugin](../README.md#install), open `/mcp`, and use
the browser sign-in flow. The bundled connection is already header-free OAuth;
there is no Authorization header to remove and no API key is required.

For claude.ai or Claude Desktop surfaces that offer custom remote connectors,
add `https://app.agent-task.com/v1/public/mcp` through that surface's connector UI.
Availability depends on the client/account. A connector provides MCP capabilities;
it does not by itself install this repository's local commands, hooks, or skills.

Tool inventory is discovered from the authenticated server and can vary by
deployment and access. Do not use a fixed tool count as a connection test.
