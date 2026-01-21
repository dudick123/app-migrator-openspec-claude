"""Unit tests for JSON Schema validator."""

import json
import tempfile
from pathlib import Path

import pytest

from argocd_migrator.exceptions import ValidationError
from argocd_migrator.validator import load_schema, validate_json

VALID_APP = {
    "apiVersion": "argoproj.io/v1alpha1",
    "kind": "Application",
    "metadata": {
        "name": "test-app"
    },
    "spec": {
        "project": "default",
        "source": {
            "repoURL": "https://github.com/test/repo"
        },
        "destination": {
            "server": "https://kubernetes.default.svc"
        }
    }
}

INVALID_API_VERSION = {
    "apiVersion": "v1",
    "kind": "Application",
    "metadata": {"name": "test"},
    "spec": {
        "project": "default",
        "source": {"repoURL": "https://github.com/test/repo"},
        "destination": {"server": "https://kubernetes.default.svc"}
    }
}

MISSING_REQUIRED_FIELD = {
    "apiVersion": "argoproj.io/v1alpha1",
    "kind": "Application",
    "metadata": {"name": "test"},
    "spec": {
        "project": "default",
        # Missing source
        "destination": {"server": "https://kubernetes.default.svc"}
    }
}


def test_load_schema():
    """Test loading JSON Schema."""
    schema = load_schema()
    assert "$schema" in schema
    assert "properties" in schema


def test_validate_valid_application():
    """Test validating a valid ArgoCD Application."""
    # Should not raise
    validate_json(VALID_APP)


def test_validate_invalid_api_version():
    """Test validation fails for invalid apiVersion."""
    with pytest.raises(ValidationError):
        validate_json(INVALID_API_VERSION)


def test_validate_missing_required_field():
    """Test validation fails for missing required fields."""
    with pytest.raises(ValidationError, match="source"):
        validate_json(MISSING_REQUIRED_FIELD)


def test_validate_json_file():
    """Test validating a JSON file."""
    from argocd_migrator.validator import validate_json_file

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(VALID_APP, f)
        f.flush()

        try:
            # Should not raise
            validate_json_file(f.name)
        finally:
            Path(f.name).unlink()


def test_validate_invalid_json_file():
    """Test validator handles invalid JSON files."""
    from argocd_migrator.validator import validate_json_file

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ invalid json ")
        f.flush()

        try:
            with pytest.raises(ValidationError, match="Invalid JSON"):
                validate_json_file(f.name)
        finally:
            Path(f.name).unlink()
