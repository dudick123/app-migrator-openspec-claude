"""Unit tests for file scanner."""

import tempfile
from pathlib import Path

import pytest

from argocd_migrator.exceptions import ScannerError
from argocd_migrator.scanner import scan_directory


def test_scan_directory_finds_yaml_files():
    """Test that scanner finds .yaml and .yml files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test files
        (tmp_path / "app1.yaml").write_text("test")
        (tmp_path / "app2.yml").write_text("test")
        (tmp_path / "readme.txt").write_text("test")

        # Create subdirectory with YAML
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "app3.yaml").write_text("test")

        # Scan
        results = scan_directory(tmp_path)

        # Should find 3 YAML files, not the txt file
        assert len(results) == 3
        assert all(f.suffix in [".yaml", ".yml"] for f in results)


def test_scan_empty_directory():
    """Test scanning a directory with no YAML files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = scan_directory(tmpdir)
        assert results == []


def test_scan_nonexistent_directory():
    """Test that scanner raises error for non-existent directory."""
    with pytest.raises(ScannerError, match="does not exist"):
        scan_directory("/nonexistent/path")


def test_scan_file_instead_of_directory():
    """Test that scanner raises error when given a file instead of directory."""
    with tempfile.NamedTemporaryFile() as tmpfile:
        with pytest.raises(ScannerError, match="not a directory"):
            scan_directory(tmpfile.name)


def test_scan_directory_sorts_results():
    """Test that scanner returns sorted file list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create files in non-alphabetical order
        (tmp_path / "z.yaml").write_text("test")
        (tmp_path / "a.yaml").write_text("test")
        (tmp_path / "m.yaml").write_text("test")

        results = scan_directory(tmp_path)
        names = [f.name for f in results]

        assert names == sorted(names)
