# Change: Update Migrator to Output Aggregated Configuration

## Why

The current migrator outputs individual JSON files for each ArgoCD Application YAML manifest. However, ArgoCD ApplicationSet generators require a single configuration file containing an array of all applications. DevOps teams need to aggregate multiple ArgoCD Application manifests into a unified `config.json` file in the ApplicationSet generator format, rather than maintaining separate JSON files for each application.

## What Changes

- Rename CLI parameter from `source` to `--input-path` for clarity
- Add aggregation capability to combine all discovered applications into a single array
- Transform ArgoCD Application manifests to simplified ApplicationSet generator config format
- Output a single `config.json` file instead of multiple individual JSON files
- Update CLI help text to reflect new aggregated output behavior
- Maintain existing validation and error reporting capabilities

## Impact

- **Breaking Change**: Output format changes from multiple JSON files to single `config.json` array
- Affected specs: `argocd-migration-pipeline` (modified capability)
- Affected code: `cli.py`, `pipeline.py`, `migrator.py`, new transformer module
- Users must update workflows expecting individual JSON files
- New use case: Direct integration with ArgoCD ApplicationSet generators
