# ADR-001: Rules Format and Usage

## Status
Accepted

## Context

The Rules format is a lightweight, human-readable format for documenting project-specific technical decisions, implementation rules, and code references. This ADR explains the Rules format so that AI assistants can understand and work with `.rules` files correctly.

## Decision

### What are Rules files?

Rules files are YAML-based specifications optimized for AI indexing and retrieval. Each `.rules` file contains project-specific technical decisions, implementation rules, and code references in a compact, maintainable format.

### Rules File Structure

A typical `.rules` file has the following structure:

```yaml
rules: "1.0"
id: "system-input-validation"  # kebab-case identifier
title: "System Input Validations"
summary: "Validate data at controllers; internal services assume data validity."
rules:
  - "Avoid repeating validations in internal services"
  - "Provide clear errors with 4xx HTTP status codes"
code_refs:  # Optional
  - "handlers/user.go"
  - "pkg/validation/*.go"
```

### Field Descriptions

- **rules**: Version of the Rules format (currently "1.0")
- **id**: Unique identifier in kebab-case format (lowercase words separated by hyphens)
- **title**: Descriptive title of the rule specification
- **summary**: Brief summary of what this specification covers
- **rules**: Array of implementation rules or guidelines (strings)
- **code_refs**: Optional array of file paths or patterns related to this specification

### Key Principles

1. **Rules do not describe what to build. They define how to build it correctly.**
2. Rules files act as a **technical contract** for implementation
3. Each file should focus on a specific technical decision or set of related rules
4. The `id` field should be descriptive and use kebab-case (e.g., "system-input-validation")

### Benefits

- **Live Context for AI**: Embedding-friendly, ideal for RAG and semantic search
- **Technical Traceability**: Clear and accessible rules without noise
- **Versionable and Incremental**: Designed for Git and continuous evolution
- **AI-Ready, Dev-Friendly**: Uses YAML without unnecessary complexity

### Usage

- Rules files are located in `docs/rules/` directory
- They are indexed in the context store collection `rules` (the project's technical rules)
- AI assistants should query `rules` collection before implementation to understand technical constraints
- Rules files complement ADRs: ADRs explain *why*, Rules files define *how*

## Consequences

### Positive
- Clear technical constraints for AI assistants
- Easy to maintain and update
- Optimized for AI context retrieval
- Supports incremental documentation

### Notes
- This ADR should be indexed in the context store collection `business-and-architecture`
- When creating new `.rules` files, follow the structure and naming conventions described here
