"""Unit tests for YAML parser."""

import tempfile
from pathlib import Path

import pytest

from argocd_migrator.exceptions import ParserError
from argocd_migrator.parser import parse_yaml_file


VALID_APP = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-app
spec:
  project: default
  source:
    repoURL: https://github.com/test/repo
  destination:
    server: https://kubernetes.default.svc
"""

INVALID_KIND = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: test
data:
  key: value
"""

MISSING_METADATA = """
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  project: default
"""

MALFORMED_YAML = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test
  invalid: [unclosed
"""


def test_parse_valid_application():
    """Test parsing a valid ArgoCD Application."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(VALID_APP)
        f.flush()

        try:
            result = parse_yaml_file(f.name)
            assert result["kind"] == "Application"
            assert result["metadata"]["name"] == "test-app"
            assert "spec" in result
        finally:
            Path(f.name).unlink()


def test_parse_invalid_kind():
    """Test that parser rejects non-Application resources."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(INVALID_KIND)
        f.flush()

        try:
            with pytest.raises(ParserError, match="not an ArgoCD Application"):
                parse_yaml_file(f.name)
        finally:
            Path(f.name).unlink()


def test_parse_missing_metadata():
    """Test that parser rejects Applications missing metadata."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(MISSING_METADATA)
        f.flush()

        try:
            with pytest.raises(ParserError, match="missing required field: metadata"):
                parse_yaml_file(f.name)
        finally:
            Path(f.name).unlink()


def test_parse_malformed_yaml():
    """Test that parser handles malformed YAML gracefully."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(MALFORMED_YAML)
        f.flush()

        try:
            with pytest.raises(ParserError, match="YAML syntax error"):
                parse_yaml_file(f.name)
        finally:
            Path(f.name).unlink()


def test_parse_nonexistent_file():
    """Test that parser raises error for non-existent files."""
    with pytest.raises(ParserError, match="does not exist"):
        parse_yaml_file("/nonexistent/file.yaml")
