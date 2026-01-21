# Project Context

## Purpose
A CLI tool for migrating ArgoCD Applications to JSON configuration format using a 4-stage pipeline architecture.

## Tech Stack
- Python 3.12+
- PyYAML, jsonschema, typer, ruff, mypy

## Project Conventions

### Code Style
[Describe your code style preferences, formatting rules, and naming conventions]

### Architecture Patterns
1. **Scanner** (✅ Current) - Discover `*.yaml`/`*.yml` files in directories
2. **Parser** (🚧 Planned) - Extract fields from valid ArgoCD Applications
3. **Migrator** (🚧 Planned) - Transform to JSON config (1:1 mapping)
4. **Validator** (🚧 Planned) - Validate against JSON Schema

### Testing Strategy
- Unit tests for each pipeline stage (Scanner, Parser, Migrator, Validator)
- Integration tests for full pipeline execution on sample directories
- Edge case tests for invalid inputs and error handling
- Use pytest with coverage reporting

### Git Workflow
- Feature branches for each pipeline stage
- Pull requests with code reviews
- Commit messages follow Conventional Commits format

## Domain Context
The ArgoCD Application Migrator is a command-line tool designed to help DevOps engineers migrate ArgoCD Application manifests from YAML to JSON configuration format. The tool will parse existing YAML files, extract relevant fields, and produce equivalent JSON files while preserving the original structure and semantics. The resulting JSON files will be validated against a predefined JSON Schema to ensure correctness. Finally, the tool will provide a summary report of the migration process, including any errors encountered.

## Important Constraints
N/A

## External Dependencies
ArgoCD API versions, JSON Schema definitions for validation
