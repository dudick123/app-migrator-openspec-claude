"""Unit tests for JSON migrator."""

import json
import tempfile
from pathlib import Path

from argocd_migrator.migrator import convert_yaml_to_json, migrate_to_json


def test_convert_yaml_to_json():
    """Test converting dictionary to JSON string."""
    data = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {"name": "test"},
        "spec": {"project": "default"},
    }

    result = convert_yaml_to_json(data)
    parsed = json.loads(result)

    assert parsed == data
    assert isinstance(result, str)


def test_migrate_to_json_creates_file():
    """Test that migrate_to_json creates output file."""
    data = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {"name": "test"},
        "spec": {"project": "default"},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.json"
        migrate_to_json(data, output_path)

        assert output_path.exists()

        # Verify content
        with open(output_path) as f:
            loaded = json.load(f)
        assert loaded == data


def test_migrate_to_json_creates_parent_dirs():
    """Test that migrate_to_json creates parent directories."""
    data = {"test": "data"}

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "subdir1" / "subdir2" / "output.json"
        migrate_to_json(data, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()


def test_migrate_preserves_nested_structures():
    """Test that migration preserves nested objects and arrays."""
    data = {
        "nested": {
            "level1": {
                "level2": {
                    "key": "value"
                }
            }
        },
        "array": [1, 2, 3],
        "mixed": [
            {"a": 1},
            {"b": 2}
        ]
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.json"
        migrate_to_json(data, output_path)

        with open(output_path) as f:
            loaded = json.load(f)

        assert loaded == data
