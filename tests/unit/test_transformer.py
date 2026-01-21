"""Unit tests for transformer module."""


from argocd_migrator.transformer import transform_to_generator_config

VALID_ARGOCD_APP = {
    "apiVersion": "argoproj.io/v1alpha1",
    "kind": "Application",
    "metadata": {
        "name": "test-app",
        "namespace": "argocd",
        "annotations": {
            "argocd.argoproj.io/sync-wave": "40"
        },
        "labels": {
            "team": "platform"
        }
    },
    "spec": {
        "project": "default",
        "source": {
            "repoURL": "https://github.com/test/repo",
            "targetRevision": "main",
            "path": "./manifests"
        },
        "destination": {
            "server": "https://kubernetes.default.svc",
            "namespace": "production"
        },
        "syncPolicy": {
            "automated": {
                "prune": True,
                "selfHeal": True
            }
        }
    }
}


def test_transform_basic_application():
    """Test transforming a basic ArgoCD Application."""
    result = transform_to_generator_config(VALID_ARGOCD_APP)

    assert result["metadata"]["name"] == "test-app"
    assert result["project"] == "default"
    assert result["source"]["repoURL"] == "https://github.com/test/repo"
    assert result["source"]["revision"] == "main"
    assert result["source"]["manifestPath"] == "./manifests"
    assert result["destination"]["clusterName"] == "in-cluster"
    assert result["destination"]["namespace"] == "production"
    assert result["enableSyncPolicy"] is True


def test_transform_metadata():
    """Test metadata transformation preserves name, annotations, labels."""
    result = transform_to_generator_config(VALID_ARGOCD_APP)

    assert "name" in result["metadata"]
    assert result["metadata"]["name"] == "test-app"

    # Check annotations
    annotations = result["metadata"].get("annotations", {})
    assert "syncWave" in annotations
    assert annotations["syncWave"] == "40"
    assert annotations["enablePrune"] is False


def test_transform_source_field_mapping():
    """Test source field mapping (targetRevision → revision, path → manifestPath)."""
    result = transform_to_generator_config(VALID_ARGOCD_APP)

    source = result["source"]
    assert "revision" in source
    assert source["revision"] == "main"
    assert "manifestPath" in source
    assert source["manifestPath"] == "./manifests"
    # Should not have old field names
    assert "targetRevision" not in source
    assert "path" not in source


def test_transform_with_directory_config():
    """Test that directory configuration is preserved."""
    app_with_directory = VALID_ARGOCD_APP.copy()
    app_with_directory["spec"]["source"]["directory"] = {"recurse": True}

    result = transform_to_generator_config(app_with_directory)

    assert "directory" in result["source"]
    assert result["source"]["directory"]["recurse"] is True


def test_transform_without_sync_policy():
    """Test enableSyncPolicy is false when syncPolicy is absent."""
    app_without_sync = VALID_ARGOCD_APP.copy()
    app_without_sync["spec"] = {
        "project": "default",
        "source": VALID_ARGOCD_APP["spec"]["source"].copy(),
        "destination": VALID_ARGOCD_APP["spec"]["destination"].copy()
    }

    result = transform_to_generator_config(app_without_sync)

    assert result["enableSyncPolicy"] is False


def test_transform_preserves_labels():
    """Test that labels are preserved in metadata."""
    result = transform_to_generator_config(VALID_ARGOCD_APP)

    assert "labels" in result["metadata"]
    assert result["metadata"]["labels"]["team"] == "platform"


def test_transform_cluster_name_mapping():
    """Test cluster name mapping from server URL."""
    app_with_custom_server = VALID_ARGOCD_APP.copy()
    app_with_custom_server["spec"]["destination"]["server"] = "https://custom-cluster.example.com:6443"

    result = transform_to_generator_config(app_with_custom_server)

    # Should derive cluster name from server URL
    assert "clusterName" in result["destination"]
    assert isinstance(result["destination"]["clusterName"], str)


def test_transform_missing_optional_fields():
    """Test transformation handles missing optional fields."""
    minimal_app = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": "minimal-app"
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

    result = transform_to_generator_config(minimal_app)

    assert result["metadata"]["name"] == "minimal-app"
    assert result["project"] == "default"
    assert result["enableSyncPolicy"] is False
