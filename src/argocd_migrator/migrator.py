"""JSON format migrator for converting YAML to JSON."""

import json
import logging
from pathlib import Path
from typing import Any

from argocd_migrator.exceptions import MigrationError

logger = logging.getLogger(__name__)


def migrate_to_json(data: dict[str, Any], output_path: str | Path) -> None:
    """
    Convert ArgoCD Application data to JSON and write to file.

    Args:
        data: Parsed ArgoCD Application dictionary
        output_path: Path where JSON file should be written

    Raises:
        MigrationError: If conversion or file writing fails
    """
    path = Path(output_path)

    try:
        # Ensure output directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON with proper formatting
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline

        logger.info(f"Migrated to JSON: {output_path}")

    except Exception as e:
        raise MigrationError(f"Error writing JSON to {output_path}: {e}") from e


def convert_yaml_to_json(yaml_data: dict[str, Any]) -> str:
    """
    Convert YAML data to JSON string.

    Args:
        yaml_data: Dictionary from parsed YAML

    Returns:
        JSON string representation

    Raises:
        MigrationError: If conversion fails
    """
    try:
        return json.dumps(yaml_data, indent=2, ensure_ascii=False)
    except Exception as e:
        raise MigrationError(f"Error converting to JSON: {e}") from e
