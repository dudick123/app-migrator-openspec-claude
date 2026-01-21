# Design: Aggregated Configuration Output

## Context

The current migrator processes ArgoCD Application manifests and outputs individual JSON files that preserve the full ArgoCD Application structure (including `apiVersion`, `kind`, etc.). However, ArgoCD ApplicationSet generators expect a simplified configuration format in a single array file.

**Current Behavior:**
- Input: `app-1.yaml`, `app-2.yaml`
- Output: `app-1.json`, `app-2.json` (separate files, full ArgoCD spec)

**Desired Behavior:**
- Input: `app-1.yaml`, `app-2.yaml`
- Output: `config.json` (single file, array of simplified configs)

**Stakeholders:**
- DevOps engineers using ApplicationSet generators
- Teams migrating from individual Applications to ApplicationSets
- CI/CD pipelines requiring aggregated configurations

## Goals / Non-Goals

**Goals:**
- Generate single `config.json` with array of application configurations
- Transform ArgoCD Application format to ApplicationSet generator config format
- Maintain field mapping accuracy during transformation
- Preserve all validation and error reporting capabilities
- Clear CLI parameter naming (`--input-path`)

**Non-Goals:**
- Supporting multiple output formats simultaneously (only aggregated config)
- Reverse transformation (config.json back to YAML)
- Processing multiple directories in single command
- Generating ArgoCD ApplicationSet resources (only the generator config)

## Decisions

### Decision: Single Aggregated Output File

**Rationale:**
- ApplicationSet generators consume a single config file
- Simpler deployment (one file vs many)
- Easier version control tracking

**Trade-offs:**
- Breaking change from current behavior
- Cannot process applications independently
- Entire batch fails if aggregation fails

### Decision: Simplified Configuration Format

**Rationale:**
- ApplicationSet generator format omits `apiVersion` and `kind`
- Flattens some nested structures for cleaner config
- Maps to generator-specific fields

**Transformation mapping:**
```
ArgoCD Application → Generator Config
-----------------------------------
metadata → metadata (with custom annotations/labels)
spec.project → project (top-level)
spec.source → source (restructured with manifestPath vs path)
spec.destination → destination (may use clusterName vs server)
spec.syncPolicy → enableSyncPolicy (boolean flag)
```

**Alternatives considered:**
- Preserve full ArgoCD structure: Rejected, not compatible with ApplicationSet generators
- Support both formats: Rejected, adds complexity and ambiguity

### Decision: In-Memory Aggregation

**Rationale:**
- Collect all parsed applications in memory before writing
- Allows validation of entire config before output
- Simpler error recovery (all-or-nothing)

**Alternatives considered:**
- Streaming write: Rejected, can't validate entire array structure
- Temporary files: Rejected, unnecessary complexity

### Decision: Rename `source` to `--input-path`

**Rationale:**
- Clearer intent (input vs output)
- Consistent with `--output-file` for single file output
- Avoids confusion with ArgoCD `source` field

## Risks / Trade-offs

**Risk: Breaking Change for Existing Users**
- **Impact:** Current users expect multiple JSON files
- **Mitigation:** Document migration path, consider version bump to 1.0.0

**Risk: Memory Usage with Large Batches**
- **Impact:** Aggregating 1000+ applications in memory
- **Mitigation:** Acceptable for typical use cases (< 100 apps), document limits

**Risk: Partial Failure Loses All Work**
- **Impact:** Single invalid app prevents entire batch from succeeding
- **Mitigation:** Provide detailed error messages, consider `--skip-invalid` flag in future

**Trade-off: Flexibility vs Simplicity**
- **Decision:** Single output format only
- **Reasoning:** Focused use case, simpler implementation
- **Cost:** Cannot support both individual and aggregated outputs

## Transformation Details

### Field Mapping

**Metadata Transformation:**
```python
# Input: ArgoCD Application metadata
metadata:
  name: example-app
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "40"
  labels:
    team: platform

# Output: Generator config metadata
metadata:
  name: example-app
  annotations:
    enablePrune: false  # derived from syncPolicy
    syncWave: "40"      # extracted from annotations
  labels:
    team: platform      # preserved
```

**Source Transformation:**
```python
# Input: ArgoCD source
source:
  repoURL: https://github.com/org/repo.git
  targetRevision: main
  path: ./manifests
  directory:
    recurse: true

# Output: Generator config source
source:
  repoURL: https://github.com/org/repo.git
  revision: main               # renamed from targetRevision
  manifestPath: ./manifests    # renamed from path
  directory:
    recurse: true              # preserved
```

**Destination Transformation:**
```python
# Input: ArgoCD destination
destination:
  server: https://kubernetes.default.svc
  namespace: default

# Output: Generator config destination (may vary)
destination:
  clusterName: cluster-name  # derived or mapped from server
  namespace: default          # preserved
```

### Output Structure

```json
[
  {
    "metadata": { "name": "app-1", "annotations": {...}, "labels": {...} },
    "project": "default",
    "source": {...},
    "destination": {...},
    "enableSyncPolicy": true
  },
  {
    "metadata": { "name": "app-2", ... },
    ...
  }
]
```

## Migration Plan

### Phase 1: Add Transformation Logic
- Implement transformer module for ArgoCD → Generator config
- Add field mapping functions
- Unit tests for transformation logic

### Phase 2: Update Pipeline
- Modify pipeline to collect all applications in memory
- Add aggregation step after parsing all files
- Update output to write single config.json

### Phase 3: Update CLI
- Rename parameter to `--input-path`
- Change `--output` to `--output-file` with default `config.json`
- Update help text and examples

### Phase 4: Update Validation
- Validate aggregated config array structure
- Update JSON Schema for generator config format
- Ensure error messages reference array indices

### Phase 5: Documentation
- Update README with new usage examples
- Document breaking changes and migration path
- Add troubleshooting for common transformation issues

## Open Questions

1. **Cluster Name Mapping:** How to derive `clusterName` from `server` URL?
   - Recommendation: Use configurable mapping file or env var

2. **SyncPolicy Transformation:** How to map complex syncPolicy to boolean `enableSyncPolicy`?
   - Recommendation: `true` if `syncPolicy.automated` exists, `false` otherwise

3. **Validation Strictness:** Should invalid apps skip or fail entire batch?
   - Recommendation: Fail entire batch (current behavior), add `--skip-invalid` in future

4. **Backward Compatibility:** Should we support a legacy mode?
   - Recommendation: No, clean break with major version bump
