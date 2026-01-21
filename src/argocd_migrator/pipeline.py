"""Pipeline orchestrator for coordinating migration stages."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from argocd_migrator.aggregator import aggregate_configs, validate_aggregated_structure
from argocd_migrator.exceptions import MigratorError
from argocd_migrator.parser import parse_yaml_file
from argocd_migrator.scanner import scan_directory
from argocd_migrator.transformer import transform_to_generator_config

logger = logging.getLogger(__name__)


@dataclass
class TransformationResult:
    """Result of transforming a single ArgoCD Application."""

    source_file: Path
    success: bool
    transformed_config: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class PipelineResult:
    """Result of aggregated pipeline execution."""

    total: int
    successful: int
    failed: int
    output_file: Path | None
    results: list[TransformationResult]

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100


def transform_file(source_file: Path) -> TransformationResult:
    """
    Parse and transform a single YAML file to generator config format.

    Args:
        source_file: Path to source YAML file

    Returns:
        TransformationResult with outcome details
    """
    try:
        # Stage 2: Parse YAML
        logger.debug(f"Parsing {source_file}")
        argocd_app = parse_yaml_file(source_file)

        # Stage 3: Transform to generator config
        logger.debug(f"Transforming {source_file}")
        config = transform_to_generator_config(argocd_app)

        logger.info(f"Successfully transformed {source_file}")
        return TransformationResult(
            source_file=source_file,
            success=True,
            transformed_config=config
        )

    except MigratorError as e:
        logger.error(f"Failed to transform {source_file}: {e}")
        return TransformationResult(
            source_file=source_file,
            success=False,
            error=str(e)
        )


def run_pipeline(
    source_dir: str | Path,
    output_file: str | Path = "config.json",
    validate: bool = True
) -> PipelineResult:
    """
    Run the full aggregated migration pipeline on a directory.

    Args:
        source_dir: Directory containing YAML files
        output_file: Path where aggregated config.json should be written
        validate: Whether to validate aggregated config (default: True)

    Returns:
        PipelineResult with summary statistics
    """
    source_path = Path(source_dir)
    output_path = Path(output_file)

    # Stage 1: Scan for YAML files
    logger.info(f"Scanning directory: {source_dir}")
    yaml_files = scan_directory(source_path)

    if not yaml_files:
        logger.warning(f"No YAML files found in {source_dir}")
        # Write empty array for empty input
        try:
            aggregate_configs([], output_path)
            return PipelineResult(
                total=0,
                successful=0,
                failed=0,
                output_file=output_path,
                results=[]
            )
        except MigratorError as e:
            logger.error(f"Failed to write empty config: {e}")
            return PipelineResult(
                total=0,
                successful=0,
                failed=0,
                output_file=None,
                results=[]
            )

    logger.info(f"Found {len(yaml_files)} YAML files to process")

    # Stage 2 & 3: Parse and transform each file
    results: list[TransformationResult] = []
    transformed_configs: list[dict[str, Any]] = []

    for yaml_file in yaml_files:
        result = transform_file(yaml_file)
        results.append(result)

        if result.success and result.transformed_config:
            transformed_configs.append(result.transformed_config)

    # Calculate statistics
    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    # If any transformation failed, don't proceed with aggregation
    if failed > 0:
        logger.error(f"Pipeline failed: {failed}/{len(results)} transformations failed")
        return PipelineResult(
            total=len(results),
            successful=successful,
            failed=failed,
            output_file=None,
            results=results
        )

    # Stage 4: Validate aggregated structure
    if validate:
        try:
            logger.debug("Validating aggregated config structure")
            validate_aggregated_structure(transformed_configs)
        except MigratorError as e:
            logger.error(f"Aggregated config validation failed: {e}")
            return PipelineResult(
                total=len(results),
                successful=0,
                failed=len(results),
                output_file=None,
                results=results
            )

    # Stage 5: Write aggregated config
    try:
        aggregate_configs(transformed_configs, output_path)
        logger.info(
            f"Pipeline complete: {successful}/{len(results)} succeeded "
            f"({(successful/len(results))*100:.1f}% success rate)"
        )

        return PipelineResult(
            total=len(results),
            successful=successful,
            failed=failed,
            output_file=output_path,
            results=results
        )

    except MigratorError as e:
        logger.error(f"Failed to write aggregated config: {e}")
        return PipelineResult(
            total=len(results),
            successful=0,
            failed=len(results),
            output_file=None,
            results=results
        )
