"""Protocol and registry for AI host integrations (one class per host)."""

from pathlib import Path
from typing import Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class AiHostIntegration(Protocol):
    """Contract for an AI host integration (Cursor, Claude Desktop, etc.)."""

    @property
    def id(self) -> str:
        """Unique identifier for this host (e.g. 'cursor', 'claude-desktop')."""
        ...

    @property
    def rules_dir(self) -> str:
        """Relative path to the rules directory (e.g. '.cursor/rules')."""
        ...

    @property
    def mcp_config_path(self) -> Optional[str]:
        """Relative path to the MCP config file for validation, or None."""
        ...

    def apply(self, target_dir: Path) -> None:
        """Create or update all config and rule files for this host under target_dir."""
        ...


_REGISTRY: Dict[str, AiHostIntegration] = {}


def register_integration(integration: AiHostIntegration) -> None:
    """Register an AI host integration by its id."""
    _REGISTRY[integration.id] = integration


def get_known_ai_tool_ids() -> List[str]:
    """Return the list of known AI tool ids (for init/validate and error messages)."""
    return list(_REGISTRY.keys())


def get_integration(ai_tool: str) -> Optional[AiHostIntegration]:
    """Return the integration for the given ai_tool id, or None if unknown."""
    return _REGISTRY.get(ai_tool)
