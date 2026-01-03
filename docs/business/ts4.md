# TS4: Technical Specs for AI

## What is TS4?

TS4 (Technical Specs for AI) is a lightweight, human-readable format for documenting technical decisions, implementation rules, and code references. It uses simple YAML files that are compact, easy to maintain, and optimized for AI indexing and retrieval.

Each TS4 file contains:
- A unique identifier in kebab-case format
- A descriptive title and summary
- A list of implementation rules or guidelines
- Optional code references to related files or modules

The format is designed to be easily understood by both AI systems (for context retrieval and code generation) and human developers (for documentation and knowledge sharing).

## Example

A typical TS4 file has the following structure:

```yaml
ts4: "1.0"
id: "system-input-validation"
title: "System Input Validations"
summary: "Validate data at controllers; internal services assume data validity."
rules:
  - "Avoid repeating validations in internal services"
  - "Provide clear errors with 4xx HTTP status codes"
code_refs:
  - "handlers/user.go"
  - "pkg/validation/*.go"
```

The `id` field uses kebab-case format (lowercase words separated by hyphens) and should be descriptive of the technical decision or rule being documented. It serves as a unique identifier for the specification and is typically derived from the title.

## Benefits

- **Live Context for AI**: Embedding-friendly, ideal for RAG and LangChain.
- **Technical Traceability**: Clear and accessible rules without noise.
- **Versionable and Incremental**: Designed for Git and continuous evolution.
- **AI-Ready, Dev-Friendly**: Uses YAML without unnecessary complexity.

## Use Cases

- **LangChain and RAG Agents**: Rapid context on decisions and rules.
- **Technical Audits**: Validations, security, structures.
- **Shared Repositories**: Clear communication between distributed teams.

## Suggested AI Prompts

### Prompt 1: Understanding TS4 Files
```
You are an assistant who understands .ts4 files. Each file contains technical decisions, implementation rules, and code references. Use this content to provide precise technical context, respecting documented rules and recommendations.
```

### Prompt 2: Technical Decision Analysis
```
Analyze the .ts4 files and explain how the described technical decisions affect the architecture and code flow, suggesting improvements if applicable.
```

### Prompt 3: Rules Summary for New Team Members
```
Based on the .ts4 files, summarize key validation and security rules for a new team member, highlighting critical dependencies.
```

## IDE Configuration

For VS Code, add the following configuration in `settings.json`:

```json
"files.associations": {
  "*.ts4": "yaml"
}
```

This allows the editor to recognize `.ts4` files as YAML and provide appropriate syntax highlighting and validation.

## Towards an Open Standard

TS4 does not replace **ADRs (Architecture Decision Records)**; it complements them as a lightweight technical specification format geared towards AI agents and intelligences.

The goal of TS4 is to become a standard for technical documentation that AI can understand and use effectively.

## Contribute

You can contribute by sharing your `.ts4` files or your experience integrating TS4 with AI tools and pipelines. Contributions help improve the standard.
