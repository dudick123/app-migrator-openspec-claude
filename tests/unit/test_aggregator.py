"""Unit tests for aggregator module."""

import json
import tempfile
from pathlib import Path

import pytest

from argocd_migrator.aggregator import aggregate_configs, validate_aggregated_structure
from argocd_migrator.exceptions import MigrationError

VALID_CONFIG_1 = {
    "metadata": {"name": "app-1"},
    "project": "default",
    "source": {"repoURL": "https://github.com/test/repo"},
    "destination": {"clusterName": "test-cluster", "namespace": "default"}
}

VALID_CONFIG_2 = {
    "metadata": {"name": "app-2"},
    "project": "production",
    "source": {"repoURL": "https://github.com/prod/repo"},
    "destination": {"clusterName": "prod-cluster", "namespace": "prod"}
}


def test_aggregate_multiple_configs():
    """Test aggregating multiple configs into a single file."""
    configs = [VALID_CONFIG_1, VALID_CONFIG_2]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "config.json"
        aggregate_configs(configs, output_file)

        assert output_file.exists()

        with open(output_file) as f:
            loaded = json.load(f)

        assert isinstance(loaded, list)
        assert len(loaded) == 2
        assert loaded[0]["metadata"]["name"] == "app-1"
        assert loaded[1]["metadata"]["name"] == "app-2"


def test_aggregate_empty_list():
    """Test aggregating empty list produces empty array."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "config.json"
        aggregate_configs([], output_file)

        assert output_file.exists()

        with open(output_file) as f:
            loaded = json.load(f)

        assert loaded == []


def test_aggregate_creates_parent_dirs():
    """Test that aggregation creates parent directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "subdir1" / "subdir2" / "config.json"
        aggregate_configs([VALID_CONFIG_1], output_file)

        assert output_file.exists()
        assert output_file.parent.exists()


def test_validate_aggregated_structure_valid():
    """Test validating a valid aggregated config list."""
    configs = [VALID_CONFIG_1, VALID_CONFIG_2]

    # Should not raise
    validate_aggregated_structure(configs)


def test_validate_aggregated_structure_not_list():
    """Test validation fails for non-list input."""
    with pytest.raises(MigrationError, match="must be a list"):
        validate_aggregated_structure({"not": "a list"})


def test_validate_aggregated_structure_missing_metadata():
    """Test validation fails for config missing metadata."""
    invalid_config = {
        "project": "default",
        "source": {"repoURL": "https://github.com/test/repo"},
        "destination": {"clusterName": "test", "namespace": "default"}
    }

    with pytest.raises(MigrationError, match="missing required field: metadata"):
        validate_aggregated_structure([invalid_config])


def test_validate_aggregated_structure_missing_name():
    """Test validation fails for metadata missing name."""
    invalid_config = {
        "metadata": {},  # Missing name
        "project": "default",
        "source": {"repoURL": "https://github.com/test/repo"},
        "destination": {"clusterName": "test", "namespace": "default"}
    }

    with pytest.raises(MigrationError, match="missing required 'name' field"):
        validate_aggregated_structure([invalid_config])


def test_validate_aggregated_structure_missing_required_fields():
    """Test validation fails for configs missing required fields."""
    configs_to_test = [
        # Missing project
        {
            "metadata": {"name": "test"},
            "source": {"repoURL": "https://github.com/test/repo"},
            "destination": {"clusterName": "test", "namespace": "default"}
        },
        # Missing source
        {
            "metadata": {"name": "test"},
            "project": "default",
            "destination": {"clusterName": "test", "namespace": "default"}
        },
        # Missing destination
        {
            "metadata": {"name": "test"},
            "project": "default",
            "source": {"repoURL": "https://github.com/test/repo"}
        }
    ]

    for invalid_config in configs_to_test:
        with pytest.raises(MigrationError, match="missing required field"):
            validate_aggregated_structure([invalid_config])


def test_validate_aggregated_structure_item_not_dict():
    """Test validation fails when config items are not dictionaries."""
    with pytest.raises(MigrationError, match="must be a dictionary"):
        validate_aggregated_structure(["not", "dictionaries"])
