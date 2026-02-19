---
rules: "1.0"
id: "ai-host-integration"
title: "AI Host Integration (Cursor, Claude Desktop)"
summary: "Cross-host rules: same MCP command, config generator sync, and checklist. Host-specific specs live in dedicated rules files (cursor-integration, claude-desktop-integration)."
---

# Rules

- |
  Supported AI hosts and host-specific specs:
  - **Cursor**: config `.cursor/mcp.json`; rules `.cursor/rules/*.mdc`. Quirks and paths: docs/rules/cursor-integration.md
  - **Claude Desktop**: config `.mcp.json` at project root; rules `.claude/rules/`; Skills support. Quirks and paths: docs/rules/claude-desktop-integration.md
  - Other MCP-compatible hosts may be added later; each gets its own config generator and, if needed, a dedicated rules file (e.g. docs/rules/<host>-integration.md)
- |
  MCP command must be consistent across hosts (MUST):
  - The command used to start the Cliplin MCP server MUST be the same for all supported hosts: use `uv run cliplin mcp` so the host runs the project's cliplin (with instructions); do not use bare `cliplin mcp` in templates, as it may resolve to a global install and cause "No server info found" or wrong version
  - In code: each AI host integration in `src/cliplin/utils/ai_host_integrations/` that writes MCP config (via `create_cursor_mcp_config` or `create_claude_desktop_mcp_config` in templates.py) MUST set the same command and args: `"command": "uv", "args": ["run", "cliplin", "mcp"]`
- |
  When changing templates or MCP-related commands (MUST):
  - When modifying MCP server startup (command, args, env), init templates that write MCP config, or CLI behavior that affects how AI hosts run Cliplin, you MUST update **all** supported host config generators in the same change
  - Update both `create_cursor_mcp_config` and `create_claude_desktop_mcp_config` in templates.py together (they are called from the integration handlers); do not change only one
  - Use the same command pattern and args for Cursor and Claude Desktop unless a host-specific quirk is documented in the host's rules file
  - If adding a new host (e.g. another IDE or MCP client), add an integration class in `src/cliplin/utils/ai_host_integrations/` following docs/rules/ai-host-integration-handler-pattern.md, use the same command pattern unless the host requires otherwise, and add a dedicated rules file (e.g. docs/rules/<host>-integration.md) or document in docs/business/framework.md
- |
  Checklist before merging changes to templates or MCP command:
  - [ ] create_cursor_mcp_config and create_claude_desktop_mcp_config in templates.py both use the same command/args
  - [ ] Command is `uv run cliplin mcp` (or documented exception)
  - [ ] Any new host has its integration class in ai_host_integrations and is listed in this rules file (and has a host-specific rules file if needed)

# Code Refs

- "src/cliplin/utils/templates.py"
- "src/cliplin/utils/ai_host_integrations/"
- "docs/rules/ai-host-integration-handler-pattern.md"
- "docs/adrs/004-mcp-server-instructions.md"
- "docs/rules/system-modules.md"
- "docs/rules/cursor-integration.md"
- "docs/rules/claude-desktop-integration.md"
- "docs/business/framework.md"
