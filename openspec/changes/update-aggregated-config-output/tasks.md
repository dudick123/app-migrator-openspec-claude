# Implementation Tasks

## 1. Create Transformation Module
- [x] 1.1 Create `src/argocd_migrator/transformer.py` module
- [x] 1.2 Implement `transform_to_generator_config()` function for ArgoCD → Generator config
- [x] 1.3 Add metadata transformation logic (preserve name, annotations, labels)
- [x] 1.4 Add source field mapping (targetRevision → revision, path → manifestPath)
- [x] 1.5 Add destination field mapping (server → clusterName when applicable)
- [x] 1.6 Add syncPolicy → enableSyncPolicy boolean transformation
- [x] 1.7 Write unit tests for all transformation functions
- [x] 1.8 Add test cases for edge cases (missing fields, empty values)

## 2. Add Aggregation Logic
- [x] 2.1 Create `src/argocd_migrator/aggregator.py` module
- [x] 2.2 Implement in-memory collection of transformed applications
- [x] 2.3 Add array structure building logic
- [x] 2.4 Implement single file output writer for config.json
- [x] 2.5 Add validation for aggregated array structure
- [x] 2.6 Write unit tests for aggregation logic
- [x] 2.7 Test with empty input (should produce empty array)

## 3. Update Pipeline Orchestration
- [x] 3.1 Modify `pipeline.py` to include transformation step after parsing
- [x] 3.2 Add aggregation step to collect all transformed configs
- [x] 3.3 Update pipeline flow: Scanner → Parser → Transformer → Aggregator → Validator
- [x] 3.4 Change output from per-file to single aggregated file
- [x] 3.5 Update error handling for transformation failures
- [x] 3.6 Modify PipelineResult to track transformed vs failed applications
- [x] 3.7 Update integration tests for new pipeline flow

## 4. Update CLI Interface
- [x] 4.1 Rename `source` parameter to `--input-path` in cli.py
- [x] 4.2 Change `--output` to `--output-file` with default value `config.json`
- [x] 4.3 Update help text for all CLI parameters
- [x] 4.4 Update CLI to call new aggregated pipeline
- [x] 4.5 Modify summary output to reflect aggregated results
- [x] 4.6 Update error messages to reference config.json instead of multiple files
- [x] 4.7 Test `--help` displays correct information

## 5. Update JSON Schema for Generator Config
- [x] 5.1 Create new schema file `application-generator-config.json`
- [x] 5.2 Define schema for simplified generator config format
- [x] 5.3 Add array validation for top-level structure
- [x] 5.4 Update validator.py to use generator config schema
- [x] 5.5 Write unit tests for schema validation with generator config
- [x] 5.6 Test validation with example config.json

## 6. Update Tests
- [x] 6.1 Update existing unit tests for modified pipeline behavior
- [x] 6.2 Add tests for transformer module
- [x] 6.3 Add tests for aggregator module
- [x] 6.4 Update integration tests to expect single config.json output
- [x] 6.5 Add test with example ArgoCD Applications from io-artifact-examples/
- [x] 6.6 Verify output matches expected format in io-artifact-examples/applicationset-generator-config/
- [x] 6.7 Add edge case tests (empty directory, single app, invalid apps)

## 7. Update Documentation
- [x] 7.1 Update README.md with new CLI parameters
- [x] 7.2 Add examples showing aggregated config output
- [x] 7.3 Document breaking changes from v0.1.0
- [x] 7.4 Add migration guide for users of previous version
- [x] 7.5 Update usage examples with `--input-path` and `--output-file`
- [x] 7.6 Document ApplicationSet generator config format
- [x] 7.7 Add troubleshooting section for transformation errors

## 8. Update Configuration and Dependencies
- [x] 8.1 Update pyproject.toml version to 1.0.0 (breaking change)
- [x] 8.2 Update CHANGELOG.md with breaking changes
- [x] 8.3 Review and update type hints for new modules
- [x] 8.4 Run mypy on all updated modules
- [x] 8.5 Run ruff on all updated modules and fix issues

## 9. Integration and End-to-End Testing
- [x] 9.1 Test with io-artifact-examples/argocd-applications/ input
- [x] 9.2 Verify output matches structure of io-artifact-examples/applicationset-generator-config/config.json
- [x] 9.3 Test error handling with invalid YAML files
- [x] 9.4 Test with empty input directory
- [x] 9.5 Validate all CLI flags work correctly
- [x] 9.6 Test verbose and quiet modes
- [x] 9.7 Ensure exit codes are correct for success/failure

## 10. Final Validation
- [x] 10.1 Run full test suite with pytest
- [x] 10.2 Verify >80% code coverage maintained
- [x] 10.3 Test CLI help output is clear and complete
- [x] 10.4 Manually test with real ArgoCD Application examples
- [x] 10.5 Validate generated config.json with ApplicationSet
- [x] 10.6 Review all error messages for clarity
- [x] 10.7 Final code review and cleanup
