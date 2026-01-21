"""File scanner for discovering YAML files."""

import logging
from pathlib import Path

from argocd_migrator.exceptions import ScannerError

logger = logging.getLogger(__name__)


def scan_directory(directory: str | Path) -> list[Path]:
    """
    Scan a directory for YAML files recursively.

    Args:
        directory: Path to the directory to scan

    Returns:
        List of Path objects for discovered YAML files

    Raises:
        ScannerError: If directory does not exist or cannot be accessed
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise ScannerError(f"Directory does not exist: {directory}")

    if not dir_path.is_dir():
        raise ScannerError(f"Path is not a directory: {directory}")

    try:
        yaml_files: list[Path] = []

        # Find all .yaml and .yml files recursively
        for pattern in ["**/*.yaml", "**/*.yml"]:
            yaml_files.extend(dir_path.glob(pattern))

        # Sort for consistent ordering
        yaml_files.sort()

        logger.info(f"Scanned {directory}: found {len(yaml_files)} YAML files")
        return yaml_files

    except PermissionError as e:
        raise ScannerError(f"Permission denied accessing directory: {directory}") from e
    except Exception as e:
        raise ScannerError(f"Error scanning directory {directory}: {e}") from e
