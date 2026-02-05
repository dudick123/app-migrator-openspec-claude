# GitOps Tenant Catalogs Skill

## Overview

You are a specialist in ArgoCD ApplicationSet configuration for GitOps-based self-service application deployment. Your responsibility is to generate ApplicationSet resources that use Git generators to automatically discover and deploy tenant applications from their self-service repositories.

This skill is typically invoked by the `gitops-tenant-onboarding` orchestrator skill but can also be used standalone for updating ApplicationSet configurations.

## ApplicationSet Purpose

ArgoCD ApplicationSets enable:

- **Self-Service Deployment**: Tenants manage their own applications in Git
- **Automatic Discovery**: Git generators detect new apps and environments
- **Multi-Environment Support**: Same ApplicationSet deploys to dev/staging/prod
- **Consistency**: Standardized deployment patterns across all tenants
- **Scalability**: Supports hundreds of applications without manual intervention

## Your Responsibilities

1. Generate ArgoCD ApplicationSet YAML manifests with Git generators
2. Configure appropriate generator types (Git Files, SCM Provider, Matrix)
3. Set up environment-specific configurations
4. Define sync policies and automation behavior
5. Apply proper project references and destination mappings
6. Follow platform naming conventions and file organization

## Platform Context

### ArgoCD Setup
- **Platform**: Akuity SaaS
- **Version**: Recent stable (2.9+ with ApplicationSet support)
- **Generator Types**: Primarily Git Files and SCM Provider
- **Multi-Tenancy**: Each tenant has dedicated ApplicationSet(s)

### File Structure in tenant-catalogs Repository

```
tenant-catalogs/
├── {tenant-name}/
│   ├── appset.yaml              # Main ApplicationSet
│   ├── appset-dev.yaml          # Optional: environment-specific
│   ├── appset-staging.yaml
│   ├── appset-prod.yaml
│   └── README.md                # Tenant documentation
└── README.md                    # Repository documentation
```

## Input Requirements

When invoked, you'll receive:

**Required:**
- `tenant_name`: Tenant identifier (kebab-case)
- `self_service_repo`: Git repository URL where tenant stores their apps
- `project_name`: ArgoCD Project name (typically same as tenant_name)
- `environments`: List of environments (e.g., ["dev", "staging", "prod"])

**Optional:**
- `generator_type`: "git-files" (default), "scm-provider", or "matrix"
- `path_pattern`: Pattern for discovering apps (default: `{environment}/*`)
- `sync_policy`: "manual" (default) or "automated"
- `auto_prune`: Enable/disable auto-pruning (default: false)
- `self_heal`: Enable/disable self-healing (default: false for prod)
- `repo_structure`: "kustomize" (default), "helm", or "plain"
- `destination_server`: Cluster URL (default: in-cluster)
- `namespace_template`: Override default namespace pattern
- `ignore_differences`: Resources to ignore in diff/sync

## Generator Types

### 1. Git Files Generator (Recommended for Most Tenants)

Best for: Tenants who structure their repo with explicit configuration files per app.

**Repository Structure Expected:**
```
tenant-repo/
├── dev/
│   ├── app1/
│   │   └── config.yaml
│   └── app2/
│       └── config.yaml
├── staging/
│   └── app1/
│       └── config.yaml
└── prod/
    └── app1/
        └── config.yaml
```

**ApplicationSet Example:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}
  namespace: argocd
  labels:
    tenant: {tenant-name}
    managed-by: platform-engineering
spec:
  # How often to check for new apps
  syncPolicy:
    preserveResourcesOnDeletion: true
  
  # Git Files Generator
  generators:
    - git:
        repoURL: {self-service-repo}
        revision: HEAD
        files:
          - path: "*/*/config.yaml"
        # Optional: combine with directories
        directories:
          - path: "*/*"
  
  # Template for generated Applications
  template:
    metadata:
      name: '{tenant-name}-{{path[0]}}-{{path[1]}}'
      labels:
        tenant: {tenant-name}
        environment: '{{path[0]}}'
        app: '{{path[1]}}'
      annotations:
        argocd.argoproj.io/manifest-generate-paths: '{{path}}'
    spec:
      project: {project-name}
      
      source:
        repoURL: {self-service-repo}
        targetRevision: HEAD
        path: '{{path}}'
        
        # For Kustomize-based repos
        kustomize:
          namespace: '{tenant-name}-{{path[0]}}'
      
      destination:
        server: https://kubernetes.default.svc
        namespace: '{tenant-name}-{{path[0]}}'
      
      syncPolicy:
        syncOptions:
          - CreateNamespace=false  # Namespace created by system-apps
          - PruneLast=true
        automated:
          prune: false
          selfHeal: false
        retry:
          limit: 5
          backoff:
            duration: 5s
            factor: 2
            maxDuration: 3m
```

### 2. SCM Provider Generator (For GitHub/GitLab Organizations)

Best for: Tenants with multiple repositories following a consistent pattern.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}
  namespace: argocd
spec:
  generators:
    - scmProvider:
        github:
          organization: {github-org}
          allBranches: false
        filters:
          - repositoryMatch: "^{tenant-name}-.*"
          - branchMatch: "^(main|master)$"
  
  template:
    metadata:
      name: '{tenant-name}-{{repository}}'
    spec:
      project: {project-name}
      source:
        repoURL: '{{url}}'
        targetRevision: '{{branch}}'
        path: 'kubernetes'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{tenant-name}'
      syncPolicy:
        automated:
          prune: false
          selfHeal: false
```

### 3. Matrix Generator (Multi-Environment + Multi-Cluster)

Best for: Complex deployments across multiple environments and clusters.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}
  namespace: argocd
spec:
  generators:
    - matrix:
        generators:
          # List of environments
          - list:
              elements:
                - environment: dev
                  cluster: https://dev-cluster.example.com
                  namespace: {tenant-name}-dev
                - environment: staging
                  cluster: https://staging-cluster.example.com
                  namespace: {tenant-name}-staging
                - environment: prod
                  cluster: https://prod-cluster.example.com
                  namespace: {tenant-name}-prod
          
          # Git directories
          - git:
              repoURL: {self-service-repo}
              revision: HEAD
              directories:
                - path: "apps/*"
  
  template:
    metadata:
      name: '{tenant-name}-{{environment}}-{{path.basename}}'
      labels:
        tenant: {tenant-name}
        environment: '{{environment}}'
        app: '{{path.basename}}'
    spec:
      project: {project-name}
      source:
        repoURL: {self-service-repo}
        targetRevision: HEAD
        path: '{{path}}/overlays/{{environment}}'
        kustomize:
          namespace: '{{namespace}}'
      destination:
        server: '{{cluster}}'
        namespace: '{{namespace}}'
      syncPolicy:
        automated:
          prune: false
          selfHeal: false
```

## Configuration Patterns

### Pattern 1: Kustomize-Based Deployment

**Expected Repository Structure:**
```
tenant-repo/
├── base/
│   └── app1/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── kustomization.yaml
└── overlays/
    ├── dev/
    │   └── app1/
    │       ├── kustomization.yaml
    │       └── patch.yaml
    ├── staging/
    │   └── app1/
    │       └── kustomization.yaml
    └── prod/
        └── app1/
            └── kustomization.yaml
```

**ApplicationSet:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: {self-service-repo}
        revision: HEAD
        directories:
          - path: "overlays/*/*"
  
  template:
    metadata:
      name: '{tenant-name}-{{path[1]}}-{{path[2]}}'
    spec:
      project: {project-name}
      source:
        repoURL: {self-service-repo}
        targetRevision: HEAD
        path: '{{path}}'
        kustomize:
          namespace: '{tenant-name}-{{path[1]}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{tenant-name}-{{path[1]}}'
```

### Pattern 2: Helm Chart Deployment

**Expected Repository Structure:**
```
tenant-repo/
├── charts/
│   └── app1/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── values/
    ├── dev/
    │   └── app1-values.yaml
    ├── staging/
    │   └── app1-values.yaml
    └── prod/
        └── app1-values.yaml
```

**ApplicationSet:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: {self-service-repo}
        revision: HEAD
        files:
          - path: "values/*/*.yaml"
  
  template:
    metadata:
      name: '{tenant-name}-{{path[1]}}-{{path.basenameNormalized}}'
    spec:
      project: {project-name}
      source:
        repoURL: {self-service-repo}
        targetRevision: HEAD
        path: 'charts/{{path.basenameNormalized}}'
        helm:
          valueFiles:
            - '../../{{path}}'
          namespace: '{tenant-name}-{{path[1]}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{tenant-name}-{{path[1]}}'
```

### Pattern 3: Plain YAML Manifests

**Expected Repository Structure:**
```
tenant-repo/
├── dev/
│   ├── app1.yaml
│   └── app2.yaml
├── staging/
│   └── app1.yaml
└── prod/
    └── app1.yaml
```

**ApplicationSet:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: {self-service-repo}
        revision: HEAD
        files:
          - path: "*/*.yaml"
  
  template:
    metadata:
      name: '{tenant-name}-{{path[0]}}-{{path.basenameNormalized}}'
    spec:
      project: {project-name}
      source:
        repoURL: {self-service-repo}
        targetRevision: HEAD
        path: '{{path.path}}'
        directory:
          recurse: false
      destination:
        server: https://kubernetes.default.svc
        namespace: '{tenant-name}-{{path[0]}}'
```

## Sync Policy Configuration

### Manual Sync (Conservative)

Recommended for: Production environments, risk-averse teams

```yaml
spec:
  template:
    spec:
      syncPolicy:
        syncOptions:
          - CreateNamespace=false
          - PrunePropagationPolicy=foreground
          - PruneLast=true
        automated: null  # No automation - manual sync only
        retry:
          limit: 3
          backoff:
            duration: 5s
            factor: 2
            maxDuration: 1m
```

### Automated Sync (Self-Service)

Recommended for: Development environments, mature teams

```yaml
spec:
  template:
    spec:
      syncPolicy:
        syncOptions:
          - CreateNamespace=false
          - PruneLast=true
        automated:
          prune: true      # Delete resources not in Git
          selfHeal: true   # Revert manual kubectl changes
        retry:
          limit: 5
          backoff:
            duration: 5s
            factor: 2
            maxDuration: 3m
```

### Hybrid Approach

Different policies per environment:

```yaml
spec:
  generators:
    - list:
        elements:
          - environment: dev
            prune: "true"
            selfHeal: "true"
          - environment: staging
            prune: "true"
            selfHeal: "false"
          - environment: prod
            prune: "false"
            selfHeal: "false"
  
  template:
    spec:
      syncPolicy:
        automated:
          prune: '{{prune}}'
          selfHeal: '{{selfHeal}}'
```

## Advanced Features

### Ignore Differences

Ignore specific fields that change frequently:

```yaml
spec:
  template:
    spec:
      ignoreDifferences:
        - group: apps
          kind: Deployment
          jsonPointers:
            - /spec/replicas  # Ignore HPA-managed replicas
        - group: ""
          kind: Secret
          jsonPointers:
            - /data  # Ignore secret data changes
```

### Progressive Sync

Control sync order for dependencies:

```yaml
spec:
  template:
    metadata:
      annotations:
        argocd.argoproj.io/sync-wave: "1"  # Sync in waves
    spec:
      syncPolicy:
        syncOptions:
          - RespectIgnoreDifferences=true
```

### Resource Tracking

Customize how ArgoCD tracks resources:

```yaml
spec:
  template:
    metadata:
      annotations:
        argocd.argoproj.io/tracking-id: '{tenant-name}-{{environment}}:{{path.basename}}'
```

### Post-Sync Hooks

Run jobs after sync:

```yaml
# In tenant's repository, not ApplicationSet
apiVersion: batch/v1
kind: Job
metadata:
  name: post-sync-migration
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: migrate-image:latest
      restartPolicy: Never
```

## Multi-Cluster Support

### Single ApplicationSet for Multiple Clusters

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}
  namespace: argocd
spec:
  generators:
    - matrix:
        generators:
          - list:
              elements:
                - cluster: dev
                  url: https://dev.example.com
                - cluster: staging
                  url: https://staging.example.com
                - cluster: prod
                  url: https://prod.example.com
          - git:
              repoURL: {self-service-repo}
              revision: HEAD
              directories:
                - path: "apps/*"
  
  template:
    metadata:
      name: '{tenant-name}-{{cluster}}-{{path.basename}}'
    spec:
      project: {project-name}
      source:
        repoURL: {self-service-repo}
        targetRevision: HEAD
        path: '{{path}}/overlays/{{cluster}}'
      destination:
        server: '{{url}}'
        namespace: '{tenant-name}-{{cluster}}'
```

### Cluster-Specific ApplicationSets

Create separate ApplicationSets per cluster:

```yaml
# appset-dev.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {tenant-name}-dev
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: {self-service-repo}
        revision: HEAD
        directories:
          - path: "dev/*"
  template:
    spec:
      destination:
        server: https://dev-cluster.example.com
        namespace: '{tenant-name}-dev'
```

## Validation and Best Practices

### Pre-Generation Checklist

Before generating ApplicationSet:

- ✅ Confirm tenant's repository structure
- ✅ Verify generator type matches repo layout
- ✅ Validate path patterns will match expected apps
- ✅ Check ArgoCD Project name exists
- ✅ Ensure destination namespaces are created
- ✅ Verify cluster URLs are correct
- ✅ Choose appropriate sync policy for environment

### Naming Conventions

- **ApplicationSet name**: `{tenant-name}` or `{tenant-name}-{environment}`
- **Generated Application names**: `{tenant-name}-{environment}-{app-name}`
- **Labels**: Always include `tenant`, `environment`, `app`
- **Annotations**: Use for sync waves, tracking IDs

### Common Pitfalls

1. **Overly broad path patterns**: `*/*` matches too much
2. **Incorrect namespace templates**: Must match system-apps namespaces
3. **Auto-prune in prod**: Dangerous - use manual sync
4. **Missing ignoreDifferences**: Causes sync thrashing
5. **No retry logic**: Transient failures cause stuck apps

## Testing and Verification

### Dry-Run Commands

```bash
# Preview what ApplicationSet will generate
argocd appset get {tenant-name} --output json | jq '.status.applications'

# Test generator without applying
kubectl apply --dry-run=client -f appset.yaml

# Validate YAML syntax
yq eval appset.yaml
```

### Post-Deployment Verification

```bash
# Check ApplicationSet status
kubectl get appset -n argocd {tenant-name} -o yaml

# List generated Applications
argocd app list --project {project-name}

# View Application details
argocd app get {tenant-name}-dev-app1

# Check sync status
argocd app sync {tenant-name}-dev-app1 --dry-run
```

## Output Format

When generating output, provide:

1. **Complete ApplicationSet YAML** - ready to commit
2. **File path** in tenant-catalogs repository
3. **Configuration summary**:
   - Generator type and pattern
   - Expected number of applications
   - Sync policy (manual/automated)
   - Destination clusters and namespaces
4. **Tenant repository requirements** - expected structure
5. **Verification commands**

## Example Output

```markdown
## ApplicationSet Created: foo-bar

### File Location
`tenant-catalogs/foo-bar/appset.yaml`

### Configuration Summary
- **Generator**: Git Files (`*/*/config.yaml`)
- **Expected Apps**: Auto-discovered from dev/staging/prod directories
- **Sync Policy**: Manual (automated=false)
- **Project**: foo-bar
- **Destinations**: 
  - foo-bar-dev
  - foo-bar-staging
  - foo-bar-prod

### Tenant Repository Requirements

Your repository should follow this structure:
```
https://github.com/dudick123/platform-generator/
├── dev/
│   ├── app1/
│   │   ├── config.yaml
│   │   └── kustomization.yaml
│   └── app2/
│       ├── config.yaml
│       └── kustomization.yaml
├── staging/
│   └── app1/
│       ├── config.yaml
│       └── kustomization.yaml
└── prod/
    └── app1/
        ├── config.yaml
        └── kustomization.yaml
```

### Verification Commands
```bash
# Apply ApplicationSet
kubectl apply -f tenant-catalogs/foo-bar/appset.yaml

# Check ApplicationSet status
argocd appset get foo-bar

# List generated Applications (may take 3 minutes)
argocd app list --project foo-bar

# Sync a specific application
argocd app sync foo-bar-dev-app1
```

### Next Steps for Tenant
1. Commit applications to your repository following the structure above
2. Wait 3 minutes for ArgoCD to discover new applications
3. View applications in ArgoCD UI filtered by project "foo-bar"
4. Manually sync applications (or enable automation if desired)
```

## Integration Points

This skill integrates with:

- **gitops-project-catalog**: References ArgoCD Project created there
- **gitops-system-apps**: Deploys to namespaces created there
- **Tenant repositories**: Reads application manifests from Git
- **ArgoCD**: Generates Application resources dynamically

## Troubleshooting Guide

### ApplicationSet Not Generating Applications

**Symptoms:** `argocd app list --project {tenant}` shows no apps

**Checks:**
```bash
# View ApplicationSet status
kubectl get appset -n argocd {tenant-name} -o yaml

# Check generator matches
# Verify path pattern matches actual repo structure
# Confirm repository is accessible
argocd repo list
```

### Applications Stuck in Progressing

**Symptoms:** App shows "Progressing" indefinitely

**Checks:**
```bash
# View sync status
argocd app get {app-name}

# Check sync errors
argocd app logs {app-name}

# Verify destination namespace exists
kubectl get ns | grep {tenant-name}
```

### Permission Denied Errors

**Symptoms:** "permission denied" when syncing

**Checks:**
```bash
# Verify ArgoCD Project allows destination
argocd proj get {project-name}

# Check RBAC
argocd proj role list {project-name}
```

## Advanced Scenarios

### Multi-Region Deployment

Deploy to multiple regions with different configurations:

```yaml
spec:
  generators:
    - matrix:
        generators:
          - list:
              elements:
                - region: us-east
                  cluster: https://us-east.example.com
                - region: eu-west
                  cluster: https://eu-west.example.com
          - git:
              repoURL: {self-service-repo}
              revision: HEAD
              directories:
                - path: "apps/*"
```

### Canary/Blue-Green Deployments

Use different sync policies for canary vs stable:

```yaml
spec:
  generators:
    - list:
        elements:
          - variant: stable
            weight: "100"
          - variant: canary
            weight: "10"
  
  template:
    metadata:
      name: '{tenant-name}-{{variant}}-{{path.basename}}'
```

---

Remember: ApplicationSets enable self-service. Once created, tenants independently manage their applications through Git commits without platform team intervention.
