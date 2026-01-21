"""JSON Schema validator for ArgoCD Applications."""

import json
import logging
from pathlib import Path
from typing import Any

import jsonschema

from argocd_migrator.exceptions import ValidationError as MigratorValidationError

logger = logging.getLogger(__name__)


def load_schema(api_version: str = "v1alpha1") -> dict[str, Any]:
    """
    Load JSON Schema for the specified API version.

    Args:
        api_version: ArgoCD API version (default: v1alpha1)

    Returns:
        JSON Schema dictionary

    Raises:
        MigratorValidationError: If schema file cannot be loaded
    """
    schema_file = Path(__file__).parent / "schemas" / f"application-{api_version}.json"

    if not schema_file.exists():
        raise MigratorValidationError(f"Schema file not found: {schema_file}")

    try:
        with open(schema_file, encoding="utf-8") as f:
            schema: dict[str, Any] = json.load(f)
            return schema
    except Exception as e:
        raise MigratorValidationError(f"Error loading schema {schema_file}: {e}") from e


def validate_json(data: dict[str, Any], schema: dict[str, Any] | None = None) -> None:
    """
    Validate JSON data against ArgoCD Application schema.

    Args:
        data: JSON data to validate
        schema: Optional schema to use (loads default if not provided)

    Raises:
        MigratorValidationError: If validation fails
    """
    if schema is None:
        schema = load_schema()

    try:
        jsonschema.validate(instance=data, schema=schema)
        logger.info("Validation passed")

    except jsonschema.ValidationError as e:
        # Format error message with path and details
        path = ".".join(str(p) for p in e.path) if e.path else "root"
        message = f"Validation error at {path}: {e.message}"
        raise MigratorValidationError(message) from e

    except jsonschema.SchemaError as e:
        raise MigratorValidationError(f"Invalid schema: {e}") from e


def validate_json_file(file_path: str | Path) -> None:
    """
    Validate a JSON file against ArgoCD Application schema.

    Args:
        file_path: Path to JSON file to validate

    Raises:
        MigratorValidationError: If file cannot be read or validation fails
    """
    path = Path(file_path)

    if not path.exists():
        raise MigratorValidationError(f"File does not exist: {file_path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        validate_json(data)
        logger.info(f"Validated {file_path}")

    except json.JSONDecodeError as e:
        raise MigratorValidationError(f"Invalid JSON in {file_path}: {e}") from e
    except MigratorValidationError:
        raise
    except Exception as e:
        raise MigratorValidationError(f"Error validating {file_path}: {e}") from e
