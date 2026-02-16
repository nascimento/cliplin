"""Cursor IDE integration: config and rules under .cursor/."""

from pathlib import Path

from rich.console import Console

from cliplin.utils import templates

console = Console()


class CursorIntegration:
    """Integration handler for Cursor: .cursor/mcp.json and .cursor/rules/*.mdc."""

    id = "cursor"
    rules_dir = ".cursor/rules"
    mcp_config_path = ".cursor/mcp.json"

    def apply(self, target_dir: Path) -> None:
        target_dir = Path(target_dir)
        rules_dir = target_dir / self.rules_dir
        rules_dir.mkdir(parents=True, exist_ok=True)

        templates.create_cursor_mcp_config(target_dir)

        config_file = ".cursor/rules/context.mdc"
        context_file = target_dir / config_file
        context_file.write_text(templates.get_cursor_context_content(), encoding="utf-8")
        console.print(f"  [green]✓[/green] Created {config_file}")

        feature_file_path = ".cursor/rules/feature-processing.mdc"
        (target_dir / feature_file_path).write_text(
            templates.get_cursor_feature_processing_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {feature_file_path}")

        protocol_file_path = ".cursor/rules/context-protocol-loading.mdc"
        (target_dir / protocol_file_path).write_text(
            templates.get_cursor_context_protocol_loading_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {protocol_file_path}")

        flow_file_path = ".cursor/rules/feature-first-flow.mdc"
        (target_dir / flow_file_path).write_text(
            templates.get_feature_first_flow_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {flow_file_path}")
