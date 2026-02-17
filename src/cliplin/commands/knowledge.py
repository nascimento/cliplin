"""Knowledge package manager command: list, add, remove, update, show, install."""

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cliplin.protocols import ContextStore, FingerprintStore
from cliplin.utils.chromadb import (
    get_context_store,
    get_document_ids_by_file_path_prefix,
)
from cliplin.utils.fingerprint import get_fingerprint_store, remove_fingerprints_by_prefix
from cliplin.utils.ai_host_integrations.base import get_integration
from cliplin.utils.knowledge import (
    add_knowledge_package_to_config,
    clone_package,
    get_config_path,
    get_knowledge_packages,
    get_package_path,
    load_config,
    remove_knowledge_package_from_config,
    remove_package_directory,
    save_config,
    update_package_checkout,
)

from cliplin.commands.reindex import (
    get_files_to_reindex,
    reindex_file,
)

console = Console()


def _reindex_and_link_skills(
    project_root: Path,
    name: str,
    source: str,
    config: dict,
) -> None:
    """Reindex a package and link skills if host integration supports it."""
    store: ContextStore = get_context_store(project_root)
    fingerprint_store: FingerprintStore = get_fingerprint_store(project_root)
    pkg_path = get_package_path(project_root, name, source)
    if store.is_initialized():
        store.ensure_collections()
        pkg_dir_arg = pkg_path.relative_to(project_root).as_posix()
        files = get_files_to_reindex(
            project_root,
            file_path=None,
            file_type=None,
            directory=pkg_dir_arg,
        )
        for f in files:
            try:
                reindex_file(store, fingerprint_store, f, project_root, verbose=False)
            except Exception:
                pass
    ai_tool = config.get("ai_tool")
    if ai_tool:
        integration = get_integration(ai_tool)
        if integration is not None and hasattr(integration, "link_knowledge_skills"):
            try:
                integration.link_knowledge_skills(project_root, pkg_path)
            except Exception:
                pass


def _require_config(project_root: Path) -> dict:
    """Load config; exit with error if cliplin.yaml missing."""
    if not get_config_path(project_root).exists():
        console.print(
            "[bold red]Error:[/bold red] Project is not initialized or config is missing.\n"
            "Run 'cliplin init' first or ensure cliplin.yaml exists at project root."
        )
        raise typer.Exit(code=1)
    return load_config(project_root)


def _find_package_entry(project_root: Path, name: str) -> dict | None:
    """Get knowledge entry by name from config; None if not found."""
    config = load_config(project_root)
    for pkg in get_knowledge_packages(config):
        if pkg["name"] == name:
            return pkg
    return None


def knowledge_list_command() -> None:
    """List knowledge packages declared in cliplin.yaml and their install status."""
    project_root = Path.cwd()
    config = load_config(project_root)
    packages = get_knowledge_packages(config)

    if not packages:
        console.print("[dim]No knowledge packages declared. Add one with: cliplin knowledge add <name> <source> <version>[/dim]")
        return

    table = Table(title="Knowledge packages")
    table.add_column("Name", style="cyan")
    table.add_column("Source", style="white")
    table.add_column("Version", style="green")
    table.add_column("Installed", style="magenta")

    for pkg in packages:
        pkg_path = get_package_path(project_root, pkg["name"], pkg["source"])
        installed = "[green]yes[/green]" if pkg_path.exists() else "[dim]no[/dim]"
        table.add_row(pkg["name"], pkg["source"], pkg["version"], installed)

    console.print(table)


def knowledge_add_command(
    name: str = typer.Argument(..., help="Package name"),
    source: str = typer.Argument(..., help="Package source (e.g. github:owner/repo)"),
    version: str = typer.Argument(..., help="Branch, tag, or commit"),
) -> None:
    """Add a knowledge package and reindex it."""
    project_root = Path.cwd()
    config = _require_config(project_root)

    try:
        clone_package(project_root, name, source, version)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error:[/bold red] Git failed: {e.stderr or e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    config = add_knowledge_package_to_config(config, name, source, version)
    save_config(project_root, config)

    # Reindex this package only (directory scope)
    store: ContextStore = get_context_store(project_root)
    fingerprint_store: FingerprintStore = get_fingerprint_store(project_root)
    if store.is_initialized():
        store.ensure_collections()
        pkg_path = get_package_path(project_root, name, source)
        # Collect files under this package that match context types
        pkg_dir_arg = pkg_path.relative_to(project_root).as_posix()
        files = get_files_to_reindex(
            project_root,
            file_path=None,
            file_type=None,
            directory=pkg_dir_arg,
        )
        for f in files:
            try:
                reindex_file(store, fingerprint_store, f, project_root, verbose=False)
            except Exception:
                pass

    # Optional: host integration may link package skills (e.g. Claude Desktop → .claude/skills)
    ai_tool = config.get("ai_tool")
    if ai_tool:
        integration = get_integration(ai_tool)
        if integration is not None and hasattr(integration, "link_knowledge_skills"):
            try:
                integration.link_knowledge_skills(project_root, pkg_path)
            except Exception:
                pass

    console.print(Panel.fit(f"[bold green]✓[/bold green] Added knowledge package [cyan]{name}[/cyan] and reindexed."))


def knowledge_remove_command(
    name: str = typer.Argument(..., help="Package name to remove"),
) -> None:
    """Remove a knowledge package and purge its documents from the context store."""
    project_root = Path.cwd()
    config = _require_config(project_root)
    entry = _find_package_entry(project_root, name)
    if not entry:
        console.print(f"[bold red]Error:[/bold red] No knowledge package named [cyan]{name}[/cyan] in cliplin.yaml.")
        raise typer.Exit(code=1)

    source = entry["source"]
    pkg_path = get_package_path(project_root, name, source)
    prefix = pkg_path.relative_to(project_root).as_posix() + "/"

    store = get_context_store(project_root)
    if store.is_initialized():
        ids_by_collection = get_document_ids_by_file_path_prefix(store, prefix)
        for coll, ids in ids_by_collection.items():
            if ids:
                store.delete_documents(coll, ids)

    remove_fingerprints_by_prefix(project_root, prefix)
    # Optional: host integration may unlink package skills (before deleting package dir)
    ai_tool = config.get("ai_tool")
    if ai_tool:
        integration = get_integration(ai_tool)
        if integration is not None and hasattr(integration, "unlink_knowledge_skills"):
            try:
                integration.unlink_knowledge_skills(project_root, pkg_path)
            except Exception:
                pass
    config = remove_knowledge_package_from_config(config, name)
    save_config(project_root, config)
    remove_package_directory(project_root, name, source)

    console.print(Panel.fit(f"[bold green]✓[/bold green] Removed knowledge package [cyan]{name}[/cyan]."))


def knowledge_update_command(
    name: str = typer.Argument(..., help="Package name to update"),
    version: str = typer.Option(None, "--version", "-v", help="New branch, tag, or commit (default: current from config)"),
) -> None:
    """Update a knowledge package to the given (or configured) version and reindex."""
    project_root = Path.cwd()
    config = _require_config(project_root)
    entry = _find_package_entry(project_root, name)
    if not entry:
        console.print(f"[bold red]Error:[/bold red] No knowledge package named [cyan]{name}[/cyan] in cliplin.yaml.")
        raise typer.Exit(code=1)

    source = entry["source"]
    ref = version or entry["version"]

    try:
        update_package_checkout(project_root, name, source, ref)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error:[/bold red] Git failed: {e.stderr or e}")
        raise typer.Exit(code=1)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    if version:
        config = add_knowledge_package_to_config(config, name, source, version)
        save_config(project_root, config)

    store = get_context_store(project_root)
    fingerprint_store = get_fingerprint_store(project_root)
    if store.is_initialized():
        store.ensure_collections()
        pkg_path = get_package_path(project_root, name, source)
        pkg_dir_arg = pkg_path.relative_to(project_root).as_posix()
        files = get_files_to_reindex(
            project_root,
            file_path=None,
            file_type=None,
            directory=pkg_dir_arg,
        )
        for f in files:
            try:
                reindex_file(store, fingerprint_store, f, project_root, verbose=False)
            except Exception:
                pass

    console.print(Panel.fit(f"[bold green]✓[/bold green] Updated knowledge package [cyan]{name}[/cyan] and reindexed."))


def knowledge_show_command(
    name: str = typer.Argument(..., help="Package name"),
) -> None:
    """Show details for a knowledge package."""
    project_root = Path.cwd()
    config = load_config(project_root)
    entry = _find_package_entry(project_root, name)
    if not entry:
        console.print(f"[bold red]Error:[/bold red] No knowledge package named [cyan]{name}[/cyan] in cliplin.yaml.")
        raise typer.Exit(code=1)

    pkg_path = get_package_path(project_root, entry["name"], entry["source"])
    console.print(f"[bold]Name:[/bold]    {entry['name']}")
    console.print(f"[bold]Source:[/bold]  {entry['source']}")
    console.print(f"[bold]Version:[/bold] {entry['version']}")
    console.print(f"[bold]Path:[/bold]   {pkg_path.relative_to(project_root)}")
    console.print(f"[bold]Installed:[/bold] [green]yes[/green]" if pkg_path.exists() else "[bold]Installed:[/bold] [dim]no[/dim]")
    if pkg_path.exists():
        # Count files in the package on disk (exclude .git); show package content, not indexed count
        file_count = sum(
            1 for _ in pkg_path.rglob("*")
            if _.is_file() and ".git" not in _.parts
        )
        console.print(f"[bold]Files:[/bold]   {file_count}")


def knowledge_install_command(
    force: bool = typer.Option(False, "--force", "-f", help="Reinstall all packages (remove + clone fresh) using configured version"),
) -> None:
    """Install all knowledge packages declared in cliplin.yaml."""
    project_root = Path.cwd()
    config = _require_config(project_root)
    packages = get_knowledge_packages(config)

    if not packages:
        console.print("[dim]No knowledge packages declared in cliplin.yaml. Add one with: cliplin knowledge add <name> <source> <version>[/dim]")
        return

    store = get_context_store(project_root)
    if store.is_initialized():
        store.ensure_collections()

    count = 0
    for pkg in packages:
        name = pkg["name"]
        source = pkg["source"]
        version = pkg["version"]
        pkg_path = get_package_path(project_root, name, source)

        if force:
            if pkg_path.exists():
                prefix = pkg_path.relative_to(project_root).as_posix() + "/"
                if store.is_initialized():
                    ids_by_collection = get_document_ids_by_file_path_prefix(store, prefix)
                    for coll, ids in ids_by_collection.items():
                        if ids:
                            store.delete_documents(coll, ids)
                remove_fingerprints_by_prefix(project_root, prefix)
                ai_tool = config.get("ai_tool")
                if ai_tool:
                    integration = get_integration(ai_tool)
                    if integration is not None and hasattr(integration, "unlink_knowledge_skills"):
                        try:
                            integration.unlink_knowledge_skills(project_root, pkg_path)
                        except Exception:
                            pass
            remove_package_directory(project_root, name, source)
            try:
                clone_package(project_root, name, source, version)
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Error[/bold red] reinstalling [cyan]{name}[/cyan]: {e.stderr or e}")
                continue
            except ValueError as e:
                console.print(f"[bold red]Error[/bold red] reinstalling [cyan]{name}[/cyan]: {e}")
                continue
        else:
            if pkg_path.exists():
                try:
                    update_package_checkout(project_root, name, source, version)
                except subprocess.CalledProcessError as e:
                    console.print(f"[bold red]Error[/bold red] updating [cyan]{name}[/cyan]: {e.stderr or e}")
                    continue
                except FileNotFoundError as e:
                    console.print(f"[bold red]Error[/bold red] updating [cyan]{name}[/cyan]: {e}")
                    continue
            else:
                try:
                    clone_package(project_root, name, source, version)
                except subprocess.CalledProcessError as e:
                    console.print(f"[bold red]Error[/bold red] installing [cyan]{name}[/cyan]: {e.stderr or e}")
                    continue
                except ValueError as e:
                    console.print(f"[bold red]Error[/bold red] installing [cyan]{name}[/cyan]: {e}")
                    continue

        _reindex_and_link_skills(project_root, name, source, config)
        count += 1

    if force:
        console.print(Panel.fit(f"[bold green]✓[/bold green] Reinstalled [cyan]{count}[/cyan] package(s)."))
    else:
        console.print(Panel.fit(f"[bold green]✓[/bold green] Installed or updated [cyan]{count}[/cyan] package(s)."))
