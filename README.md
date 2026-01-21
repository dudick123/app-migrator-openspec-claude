# ArgoCD Application Migrator

A Python CLI tool for migrating ArgoCD Application manifests from YAML to JSON configuration format using a robust 4-stage pipeline architecture.

## Features

- **4-Stage Pipeline**: Scanner → Parser → Migrator → Validator
- **Batch Processing**: Migrate entire directories of YAML files
- **JSON Schema Validation**: Ensures output conforms to ArgoCD Application schema
- **Error Handling**: Clear error messages with detailed failure reporting
- **Type-Safe**: Full type hints and mypy strict mode
- **Well-Tested**: >80% code coverage with unit and integration tests

## Installation

### Using UV (Recommended)

```bash
uv pip install argocd-migrator
```

### Using pip

```bash
pip install argocd-migrator
```

### From Source

```bash
git clone https://github.com/yourusername/argocd-migrator.git
cd argocd-migrator
uv pip install -e ".[dev]"
```

## Requirements

- Python 3.12 or higher
- Dependencies: PyYAML, jsonschema, typer

## Usage

### Basic Migration

Migrate all ArgoCD Application YAML files in a directory:

```bash
argocd-migrator migrate /path/to/yaml/files
```

This will:
1. Scan the directory for `*.yaml` and `*.yml` files
2. Parse each file as an ArgoCD Application
3. Convert to JSON format
4. Validate against JSON Schema
5. Write output to `./output/` directory

### Specify Output Directory

```bash
argocd-migrator migrate /path/to/yaml/files --output /path/to/output
```

### Skip Validation

```bash
argocd-migrator migrate /path/to/yaml/files --no-validate
```

### Verbose Output

```bash
argocd-migrator migrate /path/to/yaml/files --verbose
```

### Quiet Mode

```bash
argocd-migrator migrate /path/to/yaml/files --quiet
```

### View Version

```bash
argocd-migrator version
```

## Pipeline Stages

### Stage 1: Scanner
Discovers all YAML files (`*.yaml`, `*.yml`) recursively in the specified directory.

### Stage 2: Parser
Parses YAML files and validates they are valid ArgoCD Applications by checking:
- `apiVersion` starts with `argoproj.io/`
- `kind` is `Application`
- Required fields `metadata` and `spec` are present
- `metadata.name` is defined

### Stage 3: Migrator
Converts parsed YAML data to JSON format with:
- 1:1 field mapping (no data loss)
- Proper JSON formatting (2-space indentation)
- UTF-8 encoding
- Trailing newline

### Stage 4: Validator
Validates JSON output against JSON Schema to ensure:
- Correct structure and required fields
- Valid data types
- ArgoCD Application compliance

## Supported ArgoCD Versions

- ArgoCD v2.x (API version `argoproj.io/v1alpha1`)

## Example

**Input** (`example-app.yaml`):
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-application
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: manifests/
  destination:
    server: https://kubernetes.default.svc
    namespace: production
```

**Output** (`example-app.json`):
```json
{
  "apiVersion": "argoproj.io/v1alpha1",
  "kind": "Application",
  "metadata": {
    "name": "my-application",
    "namespace": "argocd"
  },
  "spec": {
    "project": "default",
    "source": {
      "repoURL": "https://github.com/example/repo.git",
      "targetRevision": "main",
      "path": "manifests/"
    },
    "destination": {
      "server": "https://kubernetes.default.svc",
      "namespace": "production"
    }
  }
}
```

## Known Limitations

- **YAML Anchors/Aliases**: Not supported (JSON doesn't support references)
- **ArgoCD ApplicationSets**: Not supported (future scope)
- **Other Kubernetes Resources**: Only ArgoCD Applications are migrated

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/argocd-migrator.git
cd argocd-migrator

# Install dependencies with UV
uv pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=argocd_migrator --cov-report=html

# Run specific test file
pytest tests/unit/test_scanner.py
```

### Linting and Type Checking

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src/
```

### Project Structure

```
argocd-migrator/
├── src/argocd_migrator/
│   ├── __init__.py
│   ├── __main__.py       # CLI entry point
│   ├── cli.py            # Typer CLI definitions
│   ├── pipeline.py       # Pipeline orchestrator
│   ├── scanner.py        # Stage 1: File scanner
│   ├── parser.py         # Stage 2: YAML parser
│   ├── migrator.py       # Stage 3: JSON converter
│   ├── validator.py      # Stage 4: Schema validator
│   ├── exceptions.py     # Custom exceptions
│   └── schemas/
│       └── application-v1alpha1.json
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

## Troubleshooting

### Error: "File is not an ArgoCD Application"

Your YAML file's `kind` field is not `Application`. Ensure you're migrating ArgoCD Application manifests, not other Kubernetes resources.

### Error: "YAML syntax error"

Your YAML file has syntax errors. Validate it with `yamllint` or a YAML parser before migration.

### Error: "Validation error at spec.source"

The migrated JSON is missing required fields. Check that your source YAML has all required ArgoCD Application fields (`project`, `source`, `destination`).

### Permission Errors

Ensure you have read permissions for source files and write permissions for the output directory.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Authors

ArgoCD Migrator Team

## Changelog

### v0.1.0 (Initial Release)

- 4-stage pipeline architecture
- Scanner for discovering YAML files
- Parser for validating ArgoCD Applications
- Migrator for YAML-to-JSON conversion
- Validator for JSON Schema validation
- CLI interface with Typer
- Comprehensive test suite
