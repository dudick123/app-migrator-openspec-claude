# Design: ArgoCD Application Migrator

## Context
ArgoCD Applications are typically defined as Kubernetes Custom Resources in YAML format. Organizations may need to migrate these to JSON configuration files for various reasons (tooling compatibility, validation frameworks, CI/CD integration). The migration must preserve all fields accurately while providing validation at each stage.

**Constraints:**
- Must handle valid ArgoCD Application manifests (apiVersion, kind, metadata, spec)
- Should fail fast on invalid input rather than produce incorrect output
- Must preserve all fields with 1:1 mapping (no data loss)
- Should be usable in CI/CD pipelines (non-interactive, exit codes)

**Stakeholders:**
- DevOps engineers performing migrations
- CI/CD automation systems
- Teams managing large ArgoCD deployments

## Goals / Non-Goals

**Goals:**
- Provide reliable, automated YAML-to-JSON migration for ArgoCD Applications
- Implement clear 4-stage pipeline with validation at each step
- Support directory scanning for batch migrations
- Validate output against JSON Schema
- Provide clear error messages for troubleshooting

**Non-Goals:**
- Migrating other Kubernetes resource types (focus on ArgoCD Applications only)
- Reverse migration (JSON to YAML)
- In-place editing of live ArgoCD applications
- GUI or web interface (CLI only)
- Support for ArgoCD ApplicationSets or other ArgoCD resources (future scope)

## Decisions

### Decision: 4-Stage Pipeline Architecture
**Rationale:** Separating concerns into distinct stages (Scanner → Parser → Migrator → Validator) provides:
- Clear separation of responsibilities
- Easier testing and debugging of each stage
- Ability to run stages independently for troubleshooting
- Progressive validation (fail early)

**Alternatives considered:**
- Single-pass transformation: Rejected due to reduced testability and harder error isolation
- 2-stage (Parse + Transform): Rejected because validation is critical enough to warrant separate stage

### Decision: Python as Implementation Language
**Rationale:**
- Excellent YAML/JSON libraries (PyYAML, jsonschema)
- Easy CLI creation with argparse or click
- Common in DevOps tooling ecosystem
- Good error handling and type hints support

**Alternatives considered:**
- Go: Rejected for faster development time and better YAML library support
- Bash: Rejected due to complexity of JSON Schema validation

### Decision: JSON Schema for Validation
**Rationale:**
- Industry standard for JSON validation
- Can define ArgoCD Application structure precisely
- Provides clear validation error messages
- Tooling support (jsonschema Python library)

**Alternatives considered:**
- Custom validation logic: Rejected due to maintenance burden and lack of standardization
- Pydantic models: Could be added later but JSON Schema provides sufficient validation

### Decision: Phased Implementation (Scanner First)
**Rationale:**
- Scanner is foundational and can be tested immediately
- Allows incremental development and testing
- Each stage can be validated before moving to next

## Technology Standards

### Python Version
- **Minimum:** Python 3.12+
- **Reasoning:** Type hint improvements, dict union operators, modern standard library features
- **Compatibility:** Test on Python 3.12, 3.13 and 3.14

### Package Management
- **Tool:** UV

### Core Dependencies
- **PyYAML** (>=6.0): YAML parsing and loading
  - Use `safe_load()` for security
  - Handle YAML 1.1 and 1.2 specifications
- **jsonschema** (>=4.17.0): JSON Schema validation
  - Draft 7 or Draft 2020-12 schema support
  - Detailed error reporting with ValidationError
- **typer** (>=0.9.0): CLI framework
  - Rich help text and argument validation
  - Progress bars and colored output support
  - Alternative: argparse (stdlib) for zero dependencies
- **Ruff** (>=0.0.300): Linting and formatting
  - Enforce PEP 8 compliance
  - Auto-formatting on save/commit
- **Type Checking:** mypy (>=1.0)
  - Strict mode enabled
  - Type hints for all public functions

### Development Dependencies
- **pytest** (>=7.0): Testing framework
  - Use fixtures for test data
  - Parametrized tests for multiple scenarios
- **pytest-cov**: Code coverage reporting (target: >80%)
- **mypy** (>=1.0): Static type checking
  - Strict mode enabled
  - Type hints required for all public functions
- **ruff**: Fast Python linter and formatter
  - Replace black + flake8 + isort
  - Configuration via pyproject.toml

### Code Standards
- **Type Hints:** Required for all function signatures
  - Use `typing` module (List, Dict, Optional, Union)
  - Use modern syntax where supported (PEP 604: `str | None` instead of `Optional[str]`)
- **Docstrings:** Google or NumPy style for all public APIs
  - Include Args, Returns, Raises sections
- **Error Handling:**
  - Custom exception hierarchy (ScannerError, ParserError, etc.)
  - Never use bare `except:` clauses
  - Provide context in exception messages
- **Logging:**
  - Use stdlib `logging` module
  - Structured log messages with context (file paths, stage names)
  - Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### Project Structure
```
argocd-migrator/
├── pyproject.toml          # Modern Python packaging (PEP 621)
├── README.md
├── src/
│   └── argocd_migrator/
│       ├── __init__.py
│       ├── __main__.py     # CLI entry point
│       ├── cli.py          # Click CLI definitions
│       ├── pipeline.py     # Pipeline orchestrator
│       ├── scanner.py      # Stage 1: File scanner
│       ├── parser.py       # Stage 2: YAML parser
│       ├── migrator.py     # Stage 3: JSON converter
│       ├── validator.py    # Stage 4: Schema validator
│       ├── exceptions.py   # Custom exceptions
│       └── schemas/        # JSON Schema files
│           └── application-v1alpha1.json
└── tests/
    ├── unit/
    │   ├── test_scanner.py
    │   ├── test_parser.py
    │   ├── test_migrator.py
    │   └── test_validator.py
    ├── integration/
    │   └── test_pipeline.py
    └── fixtures/
        └── argocd-apps/    # Sample YAML files
```

### Packaging
- **Tool:** Use `pyproject.toml` (PEP 621) instead of setup.py
- **Build Backend:** hatchling or setuptools>=61.0
- **Distribution:** Python package installable via `uv install argocd-migrator`
- **Entry Point:** Console script `argocd-migrator` command

### Testing Standards
- **Unit Test Coverage:** Minimum 80% line coverage
- **Integration Tests:** Full pipeline execution with real examples
- **Test Data:** Include valid and invalid ArgoCD Application manifests
- **Fixtures:** Use pytest fixtures for reusable test data and mocks
- **Assertions:** Prefer specific assertions (assertEqual, assertRaises) over generic assertTrue

### Documentation
- **README.md:** Installation, quick start, usage examples
- **Docstrings:** All public functions and classes
- **Type Hints:** Serve as inline documentation
- **CLI Help:** Comprehensive help text via Click decorators
- **CHANGELOG.md:** Track version changes following Keep a Changelog format

### Version Control
- **Semantic Versioning:** MAJOR.MINOR.PATCH (e.g., 1.0.0)
- **Git Tags:** Tag releases with `v` prefix (v1.0.0)
- **Commit Messages:** Conventional Commits format (feat:, fix:, docs:, etc.)

## Risks / Trade-offs

**Risk: ArgoCD API Version Changes**
- **Impact:** Schema validation might fail on newer ArgoCD versions
- **Mitigation:** Make schema version configurable, document supported versions

**Risk: Complex YAML Features**
- **Impact:** YAML anchors/aliases might not translate to JSON
- **Mitigation:** Document limitations, provide clear error messages for unsupported features

**Risk: Large File Processing**
- **Impact:** Memory usage for very large manifests or many files
- **Mitigation:** Process files individually, stream where possible

**Trade-off: 1:1 Mapping vs. Optimization**
- **Decision:** Strict 1:1 mapping
- **Reasoning:** Preserves exact semantics, easier to validate correctness
- **Cost:** Output JSON might not be "optimal" but will be accurate

## Migration Plan

### Phase 1: Scanner (Current)
- Implement directory traversal and YAML file discovery
- Basic file filtering (*.yaml, *.yml)
- Unit tests for scanner logic

### Phase 2: Parser
- Parse YAML files and validate ArgoCD Application structure
- Extract required fields (apiVersion, kind, metadata, spec)
- Error handling for malformed YAML

### Phase 3: Migrator
- Transform parsed data to JSON format
- Preserve field ordering where meaningful
- Handle special cases (empty values, lists, nested objects)

### Phase 4: Validator
- Implement JSON Schema validation
- Provide detailed validation error reports
- Integration tests with real ArgoCD Application examples

### Phase 5: Integration
- CLI interface with argument parsing
- Pipeline orchestration
- End-to-end testing
- Documentation and examples

## Open Questions

1. **Schema Source:** Should we maintain our own JSON Schema for ArgoCD Applications or reference an external schema?
   - Recommendation: Start with our own, version it with the tool

2. **Error Handling Strategy:** Should the tool stop on first error or collect all errors?
   - Recommendation: Configurable via CLI flag, default to fail-fast

3. **Output Location:** Should JSON files be written to same directory, separate output directory, or stdout?
   - Recommendation: Configurable output directory, default to `./output/`

4. **File Naming:** How should output JSON files be named relative to input YAML files?
   - Recommendation: Same base name, change extension (.yaml → .json)
