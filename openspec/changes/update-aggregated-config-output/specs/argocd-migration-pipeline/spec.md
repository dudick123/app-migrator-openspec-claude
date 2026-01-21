# ArgoCD Migration Pipeline - Aggregated Output

## ADDED Requirements

### Requirement: ApplicationSet Generator Configuration Transformation
The system SHALL transform ArgoCD Application manifests to ApplicationSet generator configuration format.

#### Scenario: Transform metadata fields
- **WHEN** an ArgoCD Application metadata is transformed
- **THEN** the output SHALL include name, annotations, and labels in generator config format

#### Scenario: Map source fields to generator format
- **WHEN** transforming spec.source from ArgoCD Application
- **THEN** `targetRevision` SHALL be mapped to `revision` and `path` SHALL be mapped to `manifestPath`

#### Scenario: Extract syncPolicy to boolean flag
- **WHEN** spec.syncPolicy is present with automated configuration
- **THEN** `enableSyncPolicy` SHALL be set to true in the output

#### Scenario: Transform destination fields
- **WHEN** spec.destination contains server and namespace
- **THEN** the output SHALL map to `clusterName` and `namespace` in generator config format

### Requirement: Aggregated Configuration Output
The system SHALL aggregate all discovered applications into a single JSON array file.

#### Scenario: Combine multiple applications into array
- **WHEN** multiple ArgoCD Application YAMLs are processed
- **THEN** all SHALL be combined into a single JSON array in config.json

#### Scenario: Write single output file
- **WHEN** migration completes successfully
- **THEN** a single config.json file SHALL be written containing the array of all applications

#### Scenario: Empty input directory produces empty array
- **WHEN** no valid ArgoCD Applications are found
- **THEN** config.json SHALL contain an empty array []

#### Scenario: Fail on any transformation error
- **WHEN** any application fails transformation
- **THEN** no config.json SHALL be written and detailed error SHALL be reported

### Requirement: Input Path CLI Parameter
The system SHALL accept an `--input-path` parameter to specify the directory containing ArgoCD Application manifests.

#### Scenario: Accept input-path parameter
- **WHEN** user provides `--input-path` parameter
- **THEN** the system SHALL scan that directory for YAML files

#### Scenario: Display help with input-path documentation
- **WHEN** user runs `--help` command
- **THEN** `--input-path` parameter SHALL be documented with clear description

#### Scenario: Validate input-path exists
- **WHEN** user provides non-existent input-path
- **THEN** system SHALL raise clear error indicating path does not exist

## MODIFIED Requirements

### Requirement: JSON Format Migrator
The system SHALL transform parsed ArgoCD Application data to ApplicationSet generator configuration format.

#### Scenario: Transform to generator config format
- **WHEN** an ArgoCD Application is migrated
- **THEN** output SHALL omit apiVersion and kind fields and use simplified structure

#### Scenario: Preserve required application fields
- **WHEN** transforming an application
- **THEN** metadata name, project, source, and destination SHALL be preserved with appropriate field mappings

#### Scenario: Handle optional fields appropriately
- **WHEN** optional fields like syncPolicy or directory are present
- **THEN** they SHALL be transformed to generator config equivalents (enableSyncPolicy, directory.recurse)

### Requirement: CLI Interface
The system SHALL provide a command-line interface with `--input-path` for input and `--output-file` for aggregated output.

#### Scenario: Execute migration with input-path argument
- **WHEN** user runs the CLI with `--input-path` directory
- **THEN** the tool SHALL scan, parse, transform, and aggregate all ArgoCD Applications from that directory

#### Scenario: Configure output file path
- **WHEN** user specifies `--output-file` parameter
- **THEN** aggregated config SHALL be written to the specified file path (default: config.json)

#### Scenario: Display help information
- **WHEN** user runs `--help` or `argocd-migrator --help`
- **THEN** complete usage information with all parameters SHALL be displayed

#### Scenario: Handle errors gracefully
- **WHEN** any stage fails (scanner, parser, transformer, aggregator)
- **THEN** the CLI SHALL display a clear error message and exit with a non-zero status code

#### Scenario: Display migration summary
- **WHEN** processing completes
- **THEN** the CLI SHALL display total applications processed, successful transformations, and any failures

### Requirement: Pipeline Orchestration
The system SHALL coordinate Scanner → Parser → Transformer → Aggregator → Validator stages in sequence.

#### Scenario: Execute stages in order with aggregation
- **WHEN** a migration is initiated
- **THEN** stages SHALL execute in order: Scanner → Parser → Transformer → Aggregator → Validator → Output Writer

#### Scenario: Aggregate all transformed applications
- **WHEN** all applications are transformed successfully
- **THEN** they SHALL be collected into a single array before validation

#### Scenario: Validate aggregated config structure
- **WHEN** aggregation completes
- **THEN** the entire config array SHALL be validated as a whole

#### Scenario: Fail fast on transformation errors
- **WHEN** any application transformation fails
- **THEN** aggregation SHALL not proceed and detailed error SHALL be reported with file reference
