"""Transformer for converting ArgoCD Applications to ApplicationSet generator config format."""

import logging
from typing import Any

from argocd_migrator.exceptions import MigrationError

logger = logging.getLogger(__name__)


def transform_to_generator_config(argocd_app: dict[str, Any]) -> dict[str, Any]:
    """
    Transform an ArgoCD Application to ApplicationSet generator config format.

    Args:
        argocd_app: Parsed ArgoCD Application dictionary

    Returns:
        Generator config dictionary

    Raises:
        MigrationError: If transformation fails
    """
    try:
        config: dict[str, Any] = {}

        # Transform metadata
        config["metadata"] = _transform_metadata(argocd_app.get("metadata", {}))

        # Extract project from spec
        spec = argocd_app.get("spec", {})
        config["project"] = spec.get("project", "default")

        # Transform source
        config["source"] = _transform_source(spec.get("source", {}))

        # Transform destination
        config["destination"] = _transform_destination(spec.get("destination", {}))

        # Transform syncPolicy to boolean
        config["enableSyncPolicy"] = _transform_sync_policy(spec.get("syncPolicy"))

        logger.debug(f"Transformed {config['metadata'].get('name', 'unknown')} to generator config")
        return config

    except Exception as e:
        raise MigrationError(f"Error transforming application to generator config: {e}") from e


def _transform_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Transform metadata section.

    Args:
        metadata: ArgoCD Application metadata

    Returns:
        Generator config metadata
    """
    config_metadata: dict[str, Any] = {}

    # Preserve name
    if "name" in metadata:
        config_metadata["name"] = metadata["name"]

    # Transform annotations
    annotations: dict[str, Any] = {}
    original_annotations = metadata.get("annotations", {})

    # Extract sync-wave annotation if present
    sync_wave = original_annotations.get("argocd.argoproj.io/sync-wave")
    if sync_wave:
        annotations["syncWave"] = sync_wave

    # Add enablePrune annotation (set to false by default)
    annotations["enablePrune"] = False

    # Preserve other annotations (excluding ArgoCD-specific ones)
    for key, value in original_annotations.items():
        if not key.startswith("argocd.argoproj.io/"):
            annotations[key] = value

    if annotations:
        config_metadata["annotations"] = annotations

    # Preserve labels
    if "labels" in metadata:
        config_metadata["labels"] = metadata["labels"]

    return config_metadata


def _transform_source(source: dict[str, Any]) -> dict[str, Any]:
    """
    Transform source section.

    Args:
        source: ArgoCD Application source

    Returns:
        Generator config source
    """
    config_source: dict[str, Any] = {}

    # Map repoURL (preserved)
    if "repoURL" in source:
        config_source["repoURL"] = source["repoURL"]

    # Map targetRevision → revision
    if "targetRevision" in source:
        config_source["revision"] = source["targetRevision"]

    # Map path → manifestPath
    if "path" in source:
        config_source["manifestPath"] = source["path"]

    # Preserve directory configuration
    if "directory" in source:
        config_source["directory"] = source["directory"]

    # Preserve helm configuration if present
    if "helm" in source:
        config_source["helm"] = source["helm"]

    # Preserve kustomize configuration if present
    if "kustomize" in source:
        config_source["kustomize"] = source["kustomize"]

    return config_source


def _transform_destination(destination: dict[str, Any]) -> dict[str, Any]:
    """
    Transform destination section.

    Args:
        destination: ArgoCD Application destination

    Returns:
        Generator config destination
    """
    config_destination: dict[str, Any] = {}

    # Map server → clusterName (simplified mapping)
    if "server" in destination:
        server_url = destination["server"]
        # Extract cluster name from server URL or use simplified name
        if server_url == "https://kubernetes.default.svc":
            config_destination["clusterName"] = "in-cluster"
        else:
            # Simple extraction - just use last part of URL
            # In production, this should be configurable
            config_destination["clusterName"] = _extract_cluster_name(server_url)

    # Preserve namespace
    if "namespace" in destination:
        config_destination["namespace"] = destination["namespace"]

    return config_destination


def _extract_cluster_name(server_url: str) -> str:
    """
    Extract cluster name from server URL.

    This is a simplified implementation. In production, use a configurable mapping.

    Args:
        server_url: Kubernetes server URL

    Returns:
        Cluster name
    """
    # Remove protocol
    cluster_name = server_url.replace("https://", "").replace("http://", "")
    # Remove .svc suffix if present
    cluster_name = cluster_name.replace(".svc", "")
    # Remove port if present
    if ":" in cluster_name:
        cluster_name = cluster_name.split(":")[0]
    # Replace dots and slashes with dashes
    cluster_name = cluster_name.replace(".", "-").replace("/", "-")
    return cluster_name


def _transform_sync_policy(sync_policy: dict[str, Any] | None) -> bool:
    """
    Transform syncPolicy to boolean enableSyncPolicy flag.

    Args:
        sync_policy: ArgoCD Application syncPolicy

    Returns:
        True if automated syncPolicy exists, False otherwise
    """
    if not sync_policy:
        return False

    # Check if automated sync is enabled
    return "automated" in sync_policy and sync_policy["automated"] is not None
