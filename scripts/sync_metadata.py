#!/usr/bin/env python3
"""Generate the Codex adapter metadata from the canonical plugin manifest."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agent-task"


def expected_codex_manifest():
    source = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    result = {key: source[key] for key in (
        "name", "version", "description", "author", "homepage", "repository", "license",
        "keywords",
    )}
    result.update({
        "skills": "./skills/",
        "mcpServers": "./.mcp.json",
        "interface": {
            "displayName": "AgentTask",
            "shortDescription": "Tasks, projects, reports, and crew workflows.",
            "longDescription": source["description"],
            "developerName": source["author"]["name"],
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "websiteURL": "https://www.agent-task.com",
            "defaultPrompt": [
                "Start work on an AgentTask ticket.",
                "Summarize project progress and blockers.",
                "Plan today's focus in AgentTask.",
            ],
        },
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = PLUGIN / ".codex-plugin/plugin.json"
    expected = json.dumps(expected_codex_manifest(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            parser.exit(1, "Codex metadata is stale; run python3 scripts/sync_metadata.py\n")
        print("Adapter metadata is synchronized.")
    else:
        if path.is_symlink():
            parser.exit(1, "Refusing a symlink manifest.\n")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
        print("Updated plugins/agent-task/.codex-plugin/plugin.json")


if __name__ == "__main__":
    main()
