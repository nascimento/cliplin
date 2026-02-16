"""Claude Desktop integration: config and rules under .mcp.json and .claude/."""

from pathlib import Path

from rich.console import Console

from cliplin.utils import templates

console = Console()


class ClaudeDesktopIntegration:
    """Integration handler for Claude Desktop: .mcp.json and .claude/rules/ + instructions."""

    id = "claude-desktop"
    rules_dir = ".claude/rules"
    mcp_config_path = ".mcp.json"

    def apply(self, target_dir: Path) -> None:
        target_dir = Path(target_dir)
        rules_dir = target_dir / self.rules_dir
        rules_dir.mkdir(parents=True, exist_ok=True)

        templates.create_claude_desktop_mcp_config(target_dir)

        feature_file_path = ".claude/rules/feature-processing.md"
        (target_dir / feature_file_path).write_text(
            templates.get_cursor_feature_processing_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {feature_file_path}")

        protocol_file_path = ".claude/rules/context-protocol-loading.md"
        (target_dir / protocol_file_path).write_text(
            templates.get_cursor_context_protocol_loading_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {protocol_file_path}")

        flow_file_path = ".claude/rules/feature-first-flow.md"
        (target_dir / flow_file_path).write_text(
            templates.get_feature_first_flow_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {flow_file_path}")

        context_file_path = ".claude/rules/context.md"
        (target_dir / context_file_path).write_text(
            templates.get_cursor_context_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {context_file_path}")

        instructions_path = ".claude/instructions.md"
        (target_dir / instructions_path).write_text(
            templates.get_claude_desktop_instructions_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {instructions_path}")

        claude_md_path = ".claude/claude.md"
        (target_dir / claude_md_path).write_text(
            templates.get_claude_desktop_claude_md_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {claude_md_path}")
