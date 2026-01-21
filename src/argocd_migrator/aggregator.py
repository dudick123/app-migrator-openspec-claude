"""Aggregator for combining transformed applications into a single config file."""

import json
import logging
from pathlib import Path
from typing import Any

from argocd_migrator.exceptions import MigrationError

logger = logging.getLogger(__name__)


def aggregate_configs(configs: list[dict[str, Any]], output_file: str | Path) -> None:
    """
    Aggregate multiple generator configs into a single JSON array file.

    Args:
        configs: List of generator config dictionaries
        output_file: Path where aggregated config.json should be written

    Raises:
        MigrationError: If aggregation or file writing fails
    """
    path = Path(output_file)

    try:
        # Ensure output directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write aggregated config as JSON array
        with open(path, "w", encoding="utf-8") as f:
            json.dump(configs, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline

        logger.info(f"Aggregated {len(configs)} applications to {output_file}")

    except Exception as e:
        raise MigrationError(f"Error writing aggregated config to {output_file}: {e}") from e


def validate_aggregated_structure(configs: list[dict[str, Any]]) -> None:
    """
    Validate that aggregated config list has proper structure.

    Args:
        configs: List of generator config dictionaries

    Raises:
        MigrationError: If structure is invalid
    """
    if not isinstance(configs, list):
        raise MigrationError("Aggregated config must be a list")

    for idx, config in enumerate(configs):
        if not isinstance(config, dict):
            raise MigrationError(f"Config at index {idx} must be a dictionary")

        # Check required fields
        required_fields = ["metadata", "project", "source", "destination"]
        for field in required_fields:
            if field not in config:
                name = config.get("metadata", {}).get("name", f"index {idx}")
                raise MigrationError(f"Config '{name}' missing required field: {field}")

        # Validate metadata has name
        metadata = config.get("metadata", {})
        if not metadata.get("name"):
            raise MigrationError(f"Config at index {idx} metadata missing required 'name' field")

    logger.debug(f"Validated {len(configs)} configs in aggregated structure")
