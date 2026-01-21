"""YAML parser for ArgoCD Application manifests."""

import logging
from pathlib import Path
from typing import Any

import yaml

from argocd_migrator.exceptions import ParserError

logger = logging.getLogger(__name__)


def parse_yaml_file(file_path: str | Path) -> dict[str, Any]:
    """
    Parse a YAML file and validate it as an ArgoCD Application.

    Args:
        file_path: Path to the YAML file to parse

    Returns:
        Dictionary containing the parsed ArgoCD Application

    Raises:
        ParserError: If file cannot be parsed or is not a valid ArgoCD Application
    """
    path = Path(file_path)

    if not path.exists():
        raise ParserError(f"File does not exist: {file_path}")

    if not path.is_file():
        raise ParserError(f"Path is not a file: {file_path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

    except yaml.YAMLError as e:
        raise ParserError(f"YAML syntax error in {file_path}: {e}") from e
    except Exception as e:
        raise ParserError(f"Error reading file {file_path}: {e}") from e

    if not isinstance(data, dict):
        raise ParserError(f"YAML file {file_path} does not contain a dictionary")

    # Validate required ArgoCD Application fields
    _validate_argocd_application(data, file_path)

    logger.info(f"Parsed {file_path}: {data.get('metadata', {}).get('name', 'unknown')}")
    return data


def _validate_argocd_application(data: dict[str, Any], file_path: str | Path) -> None:
    """
    Validate that the data represents a valid ArgoCD Application.

    Args:
        data: Parsed YAML data
        file_path: Path to file being validated (for error messages)

    Raises:
        ParserError: If required fields are missing or invalid
    """
    # Check kind
    kind = data.get("kind")
    if kind != "Application":
        raise ParserError(
            f"File {file_path} is not an ArgoCD Application (kind: {kind})"
        )

    # Check apiVersion
    api_version = data.get("apiVersion")
    if not api_version or not api_version.startswith("argoproj.io/"):
        raise ParserError(
            f"File {file_path} has invalid apiVersion: {api_version}"
        )

    # Check metadata
    if "metadata" not in data:
        raise ParserError(f"File {file_path} is missing required field: metadata")

    metadata = data["metadata"]
    if not isinstance(metadata, dict):
        raise ParserError(f"File {file_path} has invalid metadata (not a dictionary)")

    if "name" not in metadata:
        raise ParserError(f"File {file_path} is missing metadata.name")

    # Check spec
    if "spec" not in data:
        raise ParserError(f"File {file_path} is missing required field: spec")

    if not isinstance(data["spec"], dict):
        raise ParserError(f"File {file_path} has invalid spec (not a dictionary)")
