# ArgoCD Application Migrator

A Python CLI tool for migrating ArgoCD Application manifests from YAML to ApplicationSet generator configuration format using a robust pipeline architecture.

## Features

- **Aggregated Output**: Combines all applications into a single `config.json` array
- **ApplicationSet Generator Format**: Transforms to simplified generator config format
- **4-Stage Pipeline**: Scanner → Parser → Transformer → Aggregator → Validator
- **Batch Processing**: Process entire directories of YAML files
- **Field Mapping**: Automatic transformation (targetRevision → revision, path → manifestPath)
- **Validation**: Ensures output conforms to generator config schema
- **Error Handling**: Clear error messages with detailed failure reporting
- **Type-Safe**: Full type hints and mypy strict mode
- **Well-Tested**: Comprehensive unit and integration test coverage

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

Migrate all ArgoCD Application YAML files to aggregated ApplicationSet generator config:

```bash
argocd-migrator migrate --input-path /path/to/yaml/files
```

This will:
1. Scan the directory for `*.yaml` and `*.yml` files
2. Parse each file as an ArgoCD Application
3. Transform to ApplicationSet generator config format
4. Aggregate all configs into a single array
5. Validate the aggregated config
6. Write output to `config.json` (default)

### Specify Output File

```bash
argocd-migrator migrate --input-path /path/to/yaml/files --output-file my-config.json
```

### Short Form

```bash
argocd-migrator migrate -i /path/to/yaml/files -o my-config.json
```

### Skip Validation

```bash
argocd-migrator migrate --input-path /path/to/yaml/files --no-validate
```

### Verbose Output

```bash
argocd-migrator migrate --input-path /path/to/yaml/files --verbose
```

### Quiet Mode

```bash
argocd-migrator migrate --input-path /path/to/yaml/files --quiet
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

### Stage 3: Transformer
Transforms ArgoCD Application to ApplicationSet generator config format:
- **Field Mappings**:
  - `spec.source.targetRevision` → `source.revision`
  - `spec.source.path` → `source.manifestPath`
  - `spec.destination.server` → `destination.clusterName`
  - `spec.syncPolicy` → `enableSyncPolicy` (boolean)
- **Metadata Transformation**:
  - Extracts `argocd.argoproj.io/sync-wave` → `annotations.syncWave`
  - Adds `annotations.enablePrune` (default: false)
  - Preserves labels
- **Simplification**:
  - Removes `apiVersion` and `kind`
  - Flattens project to top-level

### Stage 4: Aggregator
Collects all transformed configs into a single JSON array.

### Stage 5: Validator
Validates aggregated config array against generator config schema to ensure:
- Correct array structure
- Required fields present in each config
- Valid data types

## Supported ArgoCD Versions

- ArgoCD v2.x (API version `argoproj.io/v1alpha1`)

## Example

**Input** (`app-1.yaml`):
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-application
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "10"
  labels:
    team: platform
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: manifests/
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
```

**Output** (`config.json`):
```json
[
  {
    "metadata": {
      "name": "my-application",
      "annotations": {
        "syncWave": "10",
        "enablePrune": false
      },
      "labels": {
        "team": "platform"
      }
    },
    "project": "default",
    "source": {
      "repoURL": "https://github.com/example/repo.git",
      "revision": "main",
      "manifestPath": "manifests/"
    },
    "destination": {
      "clusterName": "in-cluster",
      "namespace": "production"
    },
    "enableSyncPolicy": true
  }
]
```

**Note**: The output is an array containing all discovered applications, not individual files.

## Breaking Changes from v0.1.0

Version 1.0.0 introduces significant breaking changes:

### CLI Changes
- **Parameter renamed**: `source` (positional) → `--input-path` (option)
- **Parameter renamed**: `--output` → `--output-file`
- **Required parameter**: `--input-path` is now required (use `-i` shorthand)

### Output Format Changes
- **Multiple files → Single file**: Output is now a single `config.json` instead of individual JSON files
- **Full ArgoCD spec → Generator config**: Output uses simplified ApplicationSet generator config format
- **Field transformations**:
  - `targetRevision` → `revision`
  - `path` → `manifestPath`
  - `server` → `clusterName`
  - `apiVersion` and `kind` fields removed from output

### Migration Guide from v0.1.0

**Old (v0.1.0)**:
```bash
argocd-migrator migrate /path/to/yaml --output /path/to/output
# Output: /path/to/output/app-1.json, /path/to/output/app-2.json, etc.
```

**New (v1.0.0)**:
```bash
argocd-migrator migrate --input-path /path/to/yaml --output-file config.json
# Output: config.json (single aggregated array)
```

If you need the old behavior, please use v0.1.0.

## Known Limitations

- **YAML Anchors/Aliases**: Not supported (JSON doesn't support references)
- **Single Directory**: Can only process one directory at a time
- **All-or-Nothing**: If any application fails transformation, no output is generated
- **Cluster Name Mapping**: Simple mapping from server URL (configurable mapping planned for future)
- **Other Kubernetes Resources**: Only ArgoCD Applications are migrated (ApplicationSets not supported)

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
