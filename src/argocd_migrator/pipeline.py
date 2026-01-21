"""Pipeline orchestrator for coordinating migration stages."""

import logging
from dataclasses import dataclass
from pathlib import Path

from argocd_migrator.exceptions import MigratorError
from argocd_migrator.migrator import migrate_to_json
from argocd_migrator.parser import parse_yaml_file
from argocd_migrator.scanner import scan_directory
from argocd_migrator.validator import validate_json

logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """Result of a single file migration."""

    source_file: Path
    output_file: Path | None
    success: bool
    error: str | None = None


@dataclass
class PipelineResult:
    """Result of pipeline execution across multiple files."""

    total: int
    successful: int
    failed: int
    results: list[MigrationResult]

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100


def migrate_file(
    source_file: Path,
    output_dir: Path,
    validate: bool = True
) -> MigrationResult:
    """
    Migrate a single YAML file through all pipeline stages.

    Args:
        source_file: Path to source YAML file
        output_dir: Directory where JSON file should be written
        validate: Whether to validate JSON output (default: True)

    Returns:
        MigrationResult with outcome details
    """
    output_file = output_dir / source_file.with_suffix(".json").name

    try:
        # Stage 2: Parse YAML
        logger.debug(f"Parsing {source_file}")
        data = parse_yaml_file(source_file)

        # Stage 3: Migrate to JSON
        logger.debug(f"Migrating {source_file} to {output_file}")
        migrate_to_json(data, output_file)

        # Stage 4: Validate JSON (optional)
        if validate:
            logger.debug(f"Validating {output_file}")
            validate_json(data)

        logger.info(f"Successfully migrated {source_file} -> {output_file}")
        return MigrationResult(
            source_file=source_file,
            output_file=output_file,
            success=True
        )

    except MigratorError as e:
        logger.error(f"Failed to migrate {source_file}: {e}")
        return MigrationResult(
            source_file=source_file,
            output_file=None,
            success=False,
            error=str(e)
        )


def run_pipeline(
    source_dir: str | Path,
    output_dir: str | Path,
    validate: bool = True
) -> PipelineResult:
    """
    Run the full migration pipeline on a directory.

    Args:
        source_dir: Directory containing YAML files
        output_dir: Directory where JSON files should be written
        validate: Whether to validate JSON output (default: True)

    Returns:
        PipelineResult with summary statistics
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Stage 1: Scan for YAML files
    logger.info(f"Scanning directory: {source_dir}")
    yaml_files = scan_directory(source_path)

    if not yaml_files:
        logger.warning(f"No YAML files found in {source_dir}")
        return PipelineResult(total=0, successful=0, failed=0, results=[])

    logger.info(f"Found {len(yaml_files)} YAML files to migrate")

    # Process each file
    results: list[MigrationResult] = []
    for yaml_file in yaml_files:
        result = migrate_file(yaml_file, output_path, validate=validate)
        results.append(result)

    # Calculate summary statistics
    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    pipeline_result = PipelineResult(
        total=len(results),
        successful=successful,
        failed=failed,
        results=results
    )

    logger.info(
        f"Pipeline complete: {successful}/{len(results)} succeeded, "
        f"{failed} failed ({pipeline_result.success_rate:.1f}% success rate)"
    )

    return pipeline_result
