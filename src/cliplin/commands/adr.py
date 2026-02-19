"""ADR generation command for creating technical ADR prompts."""

import re
from pathlib import Path
from urllib.parse import urlparse

import typer
from rich.console import Console

console = Console()

# URL pattern for GitHub, GitLab, etc.
URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?(?:github|gitlab|bitbucket|sourceforge)\.\w+/.+"
)


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid repository URL."""
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc, result.path])
    except Exception:
        return False


def adr_generate_command(
    repository: str = typer.Argument(
        ...,
        help="Repository path (local) or URL (remote) to analyze",
    ),
) -> None:
    """Generate a structured prompt for AI to create a technical ADR from a repository."""
    project_root = Path.cwd()
    
    # Determine if input is a URL or local path
    is_url = is_valid_url(repository)
    
    if is_url:
        # Validate URL format
        if not URL_PATTERN.match(repository):
            console.print(
                f"[bold red]Error:[/bold red] Invalid repository URL format: {repository}\n"
                "Please provide a valid GitHub, GitLab, Bitbucket, or SourceForge URL."
            )
            raise typer.Exit(code=1)
        
        repository_path_or_url = repository
        repository_type = "remote"
    else:
        # Validate local path exists
        repository_path = project_root / repository
        if not repository_path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Repository path does not exist: {repository}\n"
                "Please check that the path is correct or use a valid repository URL."
            )
            raise typer.Exit(code=1)
        
        repository_path_or_url = str(repository_path.resolve())
        repository_type = "local"
    
    try:
        # Generate structured prompt
        prompt = generate_adr_prompt(
            repository=repository_path_or_url,
            repository_type=repository_type,
        )
        
        # Output prompt to stdout
        console.print(prompt)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def generate_adr_prompt(
    repository: str,
    repository_type: str,
) -> str:
    """Generate a structured prompt for AI to create a technical ADR."""
    
    prompt_parts = []
    
    # Header
    prompt_parts.append("# ADR Generation Prompt")
    prompt_parts.append("")
    prompt_parts.append("## Objective")
    prompt_parts.append("")
    prompt_parts.append(
        "Create a technical ADR documenting the repository following Cliplin framework standards. "
        "The ADR should be consistent, precise, and enable AI-assisted implementation."
    )
    prompt_parts.append("")
    
    # Repository Information
    prompt_parts.append("## Repository Information")
    prompt_parts.append("")
    if repository_type == "remote":
        prompt_parts.append(f"- **Repository URL**: `{repository}`")
        prompt_parts.append("- **Repository Type**: Remote (requires cloning)")
    else:
        prompt_parts.append(f"- **Repository Path**: `{repository}`")
        prompt_parts.append("- **Repository Type**: Local")
    prompt_parts.append("")
    
    # Analysis Steps
    prompt_parts.append("## Analysis Steps")
    prompt_parts.append("")
    prompt_parts.append("Follow these steps to analyze the repository and create the ADR:")
    prompt_parts.append("")
    prompt_parts.append("1. **Access the repository**:")
    if repository_type == "remote":
        prompt_parts.append("   - Clone the repository to a temporary location")
        prompt_parts.append("   - Navigate to the cloned repository")
    else:
        prompt_parts.append("   - Navigate to the repository path")
    prompt_parts.append("")
    prompt_parts.append("2. **Analyze repository structure**:")
    prompt_parts.append("   - Identify key files: README.md, package.json, pyproject.toml, Cargo.toml, etc.")
    prompt_parts.append("   - Identify source code files and their organization")
    prompt_parts.append("   - Identify example files and test files")
    prompt_parts.append("   - Identify configuration files")
    prompt_parts.append("")
    prompt_parts.append("3. **Extract repository metadata**:")
    prompt_parts.append("   - Name and version (from package files or repository name)")
    prompt_parts.append("   - Primary programming language")
    prompt_parts.append("   - Purpose and main functionality")
    prompt_parts.append("   - Entry points or main exports")
    prompt_parts.append("")
    prompt_parts.append("4. **Identify public API surface**:")
    prompt_parts.append("   - Public classes, functions, interfaces")
    prompt_parts.append("   - Main entry points and exports")
    prompt_parts.append("   - Configuration options and requirements")
    prompt_parts.append("")
    prompt_parts.append("5. **Analyze usage patterns**:")
    prompt_parts.append("   - Review example files to understand common usage")
    prompt_parts.append("   - Identify initialization patterns")
    prompt_parts.append("   - Identify configuration patterns")
    prompt_parts.append("   - Identify error handling patterns")
    prompt_parts.append("")
    prompt_parts.append("6. **Document dependencies**:")
    prompt_parts.append("   - Runtime dependencies and version constraints")
    prompt_parts.append("   - Development dependencies")
    prompt_parts.append("   - Peer dependencies if applicable")
    prompt_parts.append("")
    prompt_parts.append("7. **Document authentication and security** (if applicable):")
    prompt_parts.append("   - Authentication methods (API keys, OAuth, tokens, etc.)")
    prompt_parts.append("   - Credential management patterns")
    prompt_parts.append("   - Security best practices")
    prompt_parts.append("")
    if repository_type == "remote":
        prompt_parts.append("8. **Clean up**:")
        prompt_parts.append("   - Remove the cloned repository after analysis")
        prompt_parts.append("")
    
    # ADR Structure
    prompt_parts.append("## ADR Structure")
    prompt_parts.append("")
    prompt_parts.append("Create the ADR following this structure:")
    prompt_parts.append("")
    prompt_parts.append("```markdown")
    prompt_parts.append("# ADR-XXX: [Library/SDK Name]")
    prompt_parts.append("")
    prompt_parts.append("## Status")
    prompt_parts.append("Proposed")
    prompt_parts.append("")
    prompt_parts.append("## Context")
    prompt_parts.append("")
    prompt_parts.append("Explain why this library/SDK is needed in the project. Describe the problem it solves.")
    prompt_parts.append("")
    prompt_parts.append("## Decision")
    prompt_parts.append("")
    prompt_parts.append("Document the technical decision to use this library/SDK, including:")
    prompt_parts.append("- Library/SDK name and version")
    prompt_parts.append("- Rationale for choosing this library")
    prompt_parts.append("- Integration approach")
    prompt_parts.append("")
    prompt_parts.append("## Consequences")
    prompt_parts.append("")
    prompt_parts.append("### Positive")
    prompt_parts.append("- List positive consequences")
    prompt_parts.append("")
    prompt_parts.append("### Negative")
    prompt_parts.append("- List negative consequences or trade-offs")
    prompt_parts.append("")
    prompt_parts.append("## Implementation")
    prompt_parts.append("")
    prompt_parts.append("### Installation")
    prompt_parts.append("Document how to install the library (package manager, version, etc.)")
    prompt_parts.append("")
    prompt_parts.append("### Configuration")
    prompt_parts.append("Document configuration options and how to set them up")
    prompt_parts.append("")
    prompt_parts.append("### API Reference")
    prompt_parts.append("Document the main public APIs, classes, functions with their signatures")
    prompt_parts.append("")
    prompt_parts.append("### Usage Examples")
    prompt_parts.append("Provide code examples showing common usage patterns based on repository examples")
    prompt_parts.append("")
    prompt_parts.append("### Error Handling")
    prompt_parts.append("Document error types and how to handle them")
    prompt_parts.append("")
    prompt_parts.append("### Dependencies")
    prompt_parts.append("List external dependencies and version constraints")
    prompt_parts.append("")
    prompt_parts.append("## References")
    prompt_parts.append("")
    prompt_parts.append("- Repository: [repository URL or path]")
    prompt_parts.append("- Documentation: [if available]")
    prompt_parts.append("- Related ADRs: [if any]")
    prompt_parts.append("```")
    prompt_parts.append("")
    
    # Cliplin Context
    prompt_parts.append("## Cliplin Framework Context")
    prompt_parts.append("")
    prompt_parts.append("1. **Load existing context**:")
    prompt_parts.append("   - Query ChromaDB collection `business-and-architecture` for existing ADRs")
    prompt_parts.append("   - Review existing ADR patterns and format in the project")
    prompt_parts.append("   - Query `rules` collection for technical constraints (the project's implementation rules)")
    prompt_parts.append("")
    prompt_parts.append("2. **Follow project patterns**:")
    prompt_parts.append("   - Use the same ADR format as existing ADRs in the project")
    prompt_parts.append("   - Follow naming conventions (ADR-XXX format)")
    prompt_parts.append("   - Ensure consistency with other ADRs")
    prompt_parts.append("")
    prompt_parts.append("3. **Index the result**:")
    prompt_parts.append("   - After creating the ADR, save it to `docs/adrs/` directory")
    prompt_parts.append("   - Run `cliplin reindex docs/adrs/[adr-filename].md` to index it in ChromaDB")
    prompt_parts.append("   - The ADR will be indexed in the `business-and-architecture` collection")
    prompt_parts.append("")
    
    # Quality Requirements
    prompt_parts.append("## Quality Requirements")
    prompt_parts.append("")
    prompt_parts.append("The ADR must be:")
    prompt_parts.append("")
    prompt_parts.append("- **Consistent**: Follows project ADR format standards and Cliplin framework")
    prompt_parts.append("- **Precise**: Contains accurate technical details extracted from the repository")
    prompt_parts.append("- **Complete**: Includes all necessary information for AI-assisted implementation")
    prompt_parts.append("- **Actionable**: Provides clear, step-by-step guidance for using the library")
    prompt_parts.append("- **Traceable**: All information must be traceable to the repository source")
    prompt_parts.append("")
    
    return "\n".join(prompt_parts)

