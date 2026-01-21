"""Integration tests for the aggregated pipeline."""

import json
import tempfile
from pathlib import Path

from argocd_migrator.pipeline import run_pipeline

VALID_APP_YAML = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: integration-test-app
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "10"
  labels:
    team: platform
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: k8s/
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
"""

VALID_APP_WITH_DIRECTORY_YAML = """
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-with-directory
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: HEAD
    path: ./manifests
    directory:
      recurse: true
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
"""

INVALID_APP_YAML = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: not-an-app
data:
  key: value
"""


def test_aggregated_pipeline_with_valid_apps():
    """Test pipeline aggregates multiple valid applications."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create source files
        (tmp_path / "app1.yaml").write_text(VALID_APP_YAML)
        (tmp_path / "app2.yaml").write_text(VALID_APP_WITH_DIRECTORY_YAML)

        # Run pipeline
        output_file = tmp_path / "config.json"
        result = run_pipeline(tmp_path, output_file, validate=True)

        assert result.total == 2
        assert result.successful == 2
        assert result.failed == 0
        assert result.output_file == output_file
        assert output_file.exists()

        # Verify JSON content
        with open(output_file) as f:
            config = json.load(f)

        assert isinstance(config, list)
        assert len(config) == 2
        assert config[0]["metadata"]["name"] == "integration-test-app"
        assert config[0]["project"] == "default"
        assert config[0]["enableSyncPolicy"] is True
        assert config[1]["metadata"]["name"] == "app-with-directory"
        assert config[1]["source"]["directory"]["recurse"] is True


def test_aggregated_pipeline_with_invalid_app():
    """Test pipeline fails when encountering invalid app."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create valid and invalid files
        (tmp_path / "valid.yaml").write_text(VALID_APP_YAML)
        (tmp_path / "invalid.yaml").write_text(INVALID_APP_YAML)

        # Run pipeline
        output_file = tmp_path / "config.json"
        result = run_pipeline(tmp_path, output_file, validate=True)

        assert result.total == 2
        assert result.successful == 1
        assert result.failed == 1
        assert result.output_file is None  # Should not write output on failure
        assert not output_file.exists()


def test_aggregated_pipeline_empty_directory():
    """Test pipeline handles empty directories gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        output_file = tmp_path / "config.json"

        result = run_pipeline(tmp_path, output_file)

        assert result.total == 0
        assert result.successful == 0
        assert result.failed == 0
        assert result.output_file == output_file
        assert output_file.exists()

        # Should contain empty array
        with open(output_file) as f:
            config = json.load(f)
        assert config == []


def test_aggregated_pipeline_creates_output_directory():
    """Test that pipeline creates output directory if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create source file
        (tmp_path / "app.yaml").write_text(VALID_APP_YAML)

        # Output to non-existent directory
        output_file = tmp_path / "output" / "nested" / "config.json"

        result = run_pipeline(tmp_path, output_file)

        assert output_file.exists()
        assert result.successful == 1


def test_aggregated_pipeline_field_transformations():
    """Test that field transformations are correct."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        (tmp_path / "app.yaml").write_text(VALID_APP_YAML)

        output_file = tmp_path / "config.json"
        result = run_pipeline(tmp_path, output_file)

        assert result.successful == 1

        with open(output_file) as f:
            config = json.load(f)

        app_config = config[0]

        # Check field mappings
        assert "revision" in app_config["source"]
        assert app_config["source"]["revision"] == "main"
        assert "manifestPath" in app_config["source"]
        assert app_config["source"]["manifestPath"] == "k8s/"

        # Check cluster name mapping
        assert "clusterName" in app_config["destination"]
        assert app_config["destination"]["clusterName"] == "in-cluster"

        # Check annotations transformation
        annotations = app_config["metadata"].get("annotations", {})
        assert "syncWave" in annotations
        assert annotations["syncWave"] == "10"
        assert annotations["enablePrune"] is False

        # Check labels preserved
        assert "labels" in app_config["metadata"]
        assert app_config["metadata"]["labels"]["team"] == "platform"


def test_aggregated_pipeline_skip_validation():
    """Test pipeline can skip validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        (tmp_path / "app.yaml").write_text(VALID_APP_YAML)

        output_file = tmp_path / "config.json"
        result = run_pipeline(tmp_path, output_file, validate=False)

        assert result.successful == 1
        assert output_file.exists()
