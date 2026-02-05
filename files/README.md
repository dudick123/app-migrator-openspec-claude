# GitOps Tenant Onboarding Skills

A modular skill system for onboarding tenants to a multi-tenant ArgoCD platform on Azure Kubernetes Service (AKS).

## Overview

This skill system provides Claude with specialized knowledge to orchestrate tenant onboarding across your GitOps platform's three discrete Git repositories:

- **project-catalog**: ArgoCD Projects for tenant isolation and RBAC
- **system-apps**: Kubernetes control plane resources (namespaces, secrets, monitoring, API routes)
- **tenant-catalogs**: ArgoCD ApplicationSets for self-service application deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           gitops-tenant-onboarding (Orchestrator)           │
│                                                             │
│  • Parses natural language requests                         │
│  • Validates prerequisites                                  │
│  • Coordinates workflow                                     │
│  • Generates comprehensive summaries                        │
└──────────────┬────────────────┬──────────────┬──────────────┘
               │                │              │
       ┌───────▼──────┐  ┌──────▼─────┐  ┌────▼──────────┐
       │ project-     │  │ system-    │  │ tenant-       │
       │ catalog      │  │ apps       │  │ catalogs      │
       │              │  │            │  │               │
       │ ArgoCD       │  │ Namespaces │  │ ApplicationS  │
       │ Projects     │  │ ESO        │  │ ets          │
       │ RBAC         │  │ Datadog    │  │ Git          │
       │              │  │ Cert-mgr   │  │ Generators   │
       │              │  │ Kong       │  │              │
       └──────────────┘  └────────────┘  └──────────────┘
```

## Skills

### 1. gitops-tenant-onboarding (Orchestrator)

**Purpose**: Main entry point that coordinates the entire onboarding workflow

**Location**: `/mnt/skills/user/gitops-tenant-onboarding/SKILL.md`

**Responsibilities**:
- Parse tenant information from natural language
- Validate prerequisites (naming, repo access, conflicts)
- Invoke sub-skills in correct sequence
- Generate comprehensive onboarding summary
- Handle errors and rollback scenarios

**Example Usage**:
```
Act as a DevOps Engineer and onboard tenant foo-bar. The foo-bar tenant uses 
the GitHub tenant https://github.com/dudick123 and their self-service appset 
repository is https://github.com/dudick123/platform-generator
```

### 2. gitops-project-catalog (Sub-skill)

**Purpose**: Generate ArgoCD Project resources with RBAC and repository whitelisting

**Location**: `/mnt/skills/user/gitops-project-catalog/SKILL.md`

**Generates**:
- ArgoCD Project YAML with source repository whitelisting
- RBAC policies with Azure Entra ID integration
- Destination cluster and namespace restrictions
- Resource allowlists/denylists

**Output**: `project-catalog/{tenant-name}/project.yaml`

### 3. gitops-system-apps (Sub-skill)

**Purpose**: Configure control plane resources for tenant workloads

**Location**: `/mnt/skills/user/gitops-system-apps/SKILL.md`

**Generates**:
- Kubernetes namespaces with resource quotas and network policies
- External Secrets Operator (SecretStore, ExternalSecret) for Azure Key Vault
- Datadog monitoring configurations and custom monitors
- cert-manager Certificate resources for TLS
- Kong API Gateway Ingress and plugins

**Output**: Multiple files in `system-apps/` subdirectories

### 4. gitops-tenant-catalogs (Sub-skill)

**Purpose**: Generate ArgoCD ApplicationSets for self-service deployment

**Location**: `/mnt/skills/user/gitops-tenant-catalogs/SKILL.md`

**Generates**:
- ApplicationSet with Git generator (Files, SCM Provider, or Matrix)
- Environment-specific sync policies
- Multi-cluster destination mappings
- Self-healing and auto-prune configurations

**Output**: `tenant-catalogs/{tenant-name}/appset.yaml`

## Workflow

### Standard Onboarding Flow

1. **User Prompt** → Orchestrator skill
   ```
   Onboard tenant acme-corp with repository https://github.com/acme/apps
   ```

2. **Orchestrator** parses and validates:
   - tenant_name: "acme-corp"
   - github_org: "acme"
   - repo: "https://github.com/acme/apps"
   - environments: ["dev", "staging", "prod"] (default)

3. **Orchestrator** invokes sub-skills in sequence:

   a. **project-catalog skill**:
      - Creates ArgoCD Project: `acme-corp`
      - Whitelists: `https://github.com/acme/apps`
      - Sets destinations: `acme-corp-dev`, `acme-corp-staging`, `acme-corp-prod`
      - Configures RBAC: `aks-acme-corp-devs`, `aks-acme-corp-admins`

   b. **system-apps skill**:
      - Creates namespaces: `acme-corp-{dev,staging,prod}`
      - Configures External Secrets for Azure Key Vault
      - Sets up Datadog monitoring annotations
      - Creates wildcard certificates: `*.acme-corp.{env}.example.com`
      - Configures Kong Ingress routes

   c. **tenant-catalogs skill**:
      - Generates ApplicationSet with Git Files generator
      - References ArgoCD Project: `acme-corp`
      - Discovers apps from: `https://github.com/acme/apps`
      - Maps to namespaces: `acme-corp-{environment}`

4. **Orchestrator** generates summary with:
   - All files created and their locations
   - Git commands to commit changes
   - ArgoCD verification commands
   - Azure prerequisites (Key Vault, Managed Identity, Entra ID groups)
   - Next steps for platform team and tenant

## Installation

### Option 1: Claude.ai Skills (Recommended)

1. Open Claude.ai
2. Go to Settings → Skills
3. Create a new skill for each SKILL.md file:
   - `gitops-tenant-onboarding` → Upload `/home/claude/gitops-tenant-onboarding/SKILL.md`
   - `gitops-project-catalog` → Upload `/home/claude/gitops-project-catalog/SKILL.md`
   - `gitops-system-apps` → Upload `/home/claude/gitops-system-apps/SKILL.md`
   - `gitops-tenant-catalogs` → Upload `/home/claude/gitops-tenant-catalogs/SKILL.md`

### Option 2: Local Development

Copy the skill directories to your skills folder:
```bash
cp -r gitops-tenant-onboarding /mnt/skills/user/
cp -r gitops-project-catalog /mnt/skills/user/
cp -r gitops-system-apps /mnt/skills/user/
cp -r gitops-tenant-catalogs /mnt/skills/user/
```

## Usage Examples

### Example 1: Basic Onboarding

**Prompt**:
```
Act as a DevOps Engineer and onboard tenant foo-bar. The foo-bar tenant uses 
the GitHub tenant https://github.com/dudick123 and their self-service appset 
repository is https://github.com/dudick123/platform-generator
```

**Result**:
- ArgoCD Project: `foo-bar`
- Namespaces: `foo-bar-dev`, `foo-bar-staging`, `foo-bar-prod`
- External Secrets from platform Key Vault
- Basic Datadog monitoring
- ApplicationSet with Git Files generator

### Example 2: Custom Requirements

**Prompt**:
```
Onboard tenant acme-corp with repo https://github.com/acme/apps. They need:
- Only dev and prod environments (no staging)
- Kong API routes for *.acme.example.com
- External secrets from Azure Key Vault "acme-kv"
- Custom Azure AD group: "aks-acme-platform-team"
- Automated sync in dev, manual in prod
```

**Result**:
- ArgoCD Project: `acme-corp` with custom Azure AD group
- Namespaces: `acme-corp-dev`, `acme-corp-prod`
- External Secrets from dedicated Key Vault: `acme-kv`
- Kong Ingress with custom domain routes
- ApplicationSet with environment-specific sync policies

### Example 3: Update Existing Tenant

**Prompt**:
```
Update tenant foo-bar to add a new staging environment and enable automated 
sync with self-healing
```

**Result**:
- Updated ArgoCD Project destinations
- New namespace: `foo-bar-staging`
- New External Secrets for staging
- Updated ApplicationSet with automated sync enabled

### Example 4: Standalone Sub-skill Usage

**Prompt to project-catalog skill**:
```
Create an ArgoCD Project for tenant test-app with source repo 
https://github.com/test/app and destinations: test-app-dev and test-app-prod
```

**Result**:
- Single ArgoCD Project YAML
- No orchestration, just the specific resource

## Customization

### Platform-Specific Configuration

Edit the skills to match your platform:

**In all skills:**
- Update cluster URLs (currently: `https://kubernetes.default.svc`)
- Modify naming conventions if different
- Adjust resource quota defaults

**In gitops-system-apps skill:**
- Change Azure Key Vault names
- Update Datadog monitoring patterns
- Modify cert-manager ClusterIssuer references
- Adjust Kong Ingress class and annotations
- Update network policy templates

**In gitops-tenant-catalogs skill:**
- Change default generator type
- Modify path patterns for your repo structure
- Adjust sync policy defaults per environment

### Adding New Features

To add new functionality:

1. **Add to system-apps skill** if it's a control plane resource
2. **Add to tenant-catalogs skill** if it's application-related
3. **Update orchestrator skill** to invoke new capabilities
4. **Update project-catalog skill** if RBAC changes needed

Example: Adding Prometheus monitoring

1. Create new section in `gitops-system-apps/SKILL.md`:
   ```markdown
   ## 6. Prometheus Configuration
   
   ### ServiceMonitor Template
   [Add ServiceMonitor YAML template]
   ```

2. Update orchestrator to include Prometheus in workflow

## Validation

### Before Onboarding

The orchestrator validates:
- ✅ Tenant name follows conventions (lowercase, kebab-case)
- ✅ GitHub repository URL is valid and accessible
- ✅ Tenant name doesn't conflict with existing tenants
- ✅ Azure Entra ID groups exist (or flag for creation)

### After Onboarding

Verify with these commands:

```bash
# Check ArgoCD Project
argocd proj get {tenant-name}

# List generated Applications
argocd app list --project {tenant-name}

# Verify namespaces
kubectl get ns | grep {tenant-name}

# Check External Secrets
kubectl get secretstore,externalsecret -n {tenant-name}-dev

# View certificates
kubectl get certificate -n {tenant-name}-dev

# Check Kong Ingress
kubectl get ingress -n {tenant-name}-dev
```

## Troubleshooting

### Common Issues

**Issue**: ApplicationSet not generating Applications

**Solution**: Check generator path pattern matches tenant's repo structure
```bash
kubectl get appset -n argocd {tenant-name} -o yaml
# Inspect .status.conditions for errors
```

**Issue**: External Secrets not syncing

**Solution**: Verify Azure Workload Identity and Key Vault access
```bash
kubectl get externalsecret -n {tenant-name}-dev
kubectl describe externalsecret {secret-name} -n {tenant-name}-dev
```

**Issue**: Certificate not issuing

**Solution**: Check cert-manager challenges and DNS
```bash
kubectl get certificate,certificaterequest,challenge -n {tenant-name}-dev
kubectl describe certificate {cert-name} -n {tenant-name}-dev
```

**Issue**: Kong Ingress not routing

**Solution**: Verify Ingress controller and backend service
```bash
kubectl get ingress -n {tenant-name}-dev
kubectl describe ingress {ingress-name} -n {tenant-name}-dev
kubectl get svc -n {tenant-name}-dev
```

### Debugging Skills

If Claude isn't using skills correctly:

1. **Check skill is loaded**: Ask "What skills do you have available?"
2. **Verify invocation**: Skills should auto-invoke when relevant
3. **Review output**: Sub-skills should produce YAML, orchestrator produces summaries
4. **Test individually**: Try invoking sub-skills directly

## Best Practices

### For Platform Team

1. **Review before committing**: Always review generated YAML before pushing to Git
2. **Test in dev first**: Onboard test tenants to verify configurations
3. **Version control**: Keep all skills in Git alongside your platform repos
4. **Document exceptions**: Add comments for non-standard configurations
5. **Automate validation**: Use pre-commit hooks to validate YAML syntax
6. **Monitor usage**: Track which tenants use which features

### For Tenants

1. **Follow repo structure**: Match the pattern expected by ApplicationSet
2. **Use Kustomize**: Recommended for environment-specific configurations
3. **Test locally**: Validate manifests with `kubectl apply --dry-run`
4. **Start simple**: Begin with basic deployments, add complexity gradually
5. **Monitor ArgoCD**: Watch for sync failures and out-of-sync resources
6. **GitOps discipline**: Make all changes via Git, not `kubectl`

## Platform Integration

### With Existing Automation

These skills complement existing platform automation:

- **Python CLI (Typer)**: Skills can generate configs for CLI processing
- **Pydantic validation**: Skills follow same validation patterns
- **Azure DevOps**: Skills generate resources compatible with pipelines
- **ServiceNow**: Skills can include change management references

### With Monitoring and Alerting

Skills generate configurations that integrate with:

- **Datadog**: Automatic namespace monitoring and custom monitors
- **Azure Monitor**: Workload Identity for metrics ingestion
- **PagerDuty**: Via Datadog alert routing
- **Slack**: ArgoCD notifications for sync events

## Maintenance

### Updating Skills

When platform changes:

1. Update relevant SKILL.md file(s)
2. Test with example tenant onboarding
3. Upload updated skill to Claude.ai
4. Communicate changes to team

### Versioning

Track skill versions in Git:
```
v1.0.0 - Initial release
v1.1.0 - Added Prometheus support
v1.2.0 - Multi-cluster ApplicationSets
```

## Security Considerations

### Secrets Management

- Skills never generate actual secret values
- External Secrets references only, not inline secrets
- Azure Key Vault for all sensitive data
- Workload Identity, not static credentials

### RBAC

- Least-privilege principle in ArgoCD Projects
- Azure Entra ID group-based access
- No cluster-admin roles for tenants
- Resource quotas to prevent abuse

### Network Isolation

- Network policies in all namespaces
- Kong rate limiting on all routes
- Private endpoints for Azure services
- Default-deny ingress policies

## Support

### Getting Help

- Platform Engineering team: [contact info]
- Documentation: [wiki URL]
- Slack: #platform-engineering
- Issues: [GitHub/ADO repo]

### Contributing

To improve these skills:

1. Fork/clone the skills repository
2. Make changes to SKILL.md files
3. Test with real tenant onboarding scenarios
4. Submit PR with description of improvements
5. Update version and changelog

## License

Internal use only - Proprietary to [Your Organization]

## Acknowledgments

Built for a mature AKS GitOps platform supporting ~100 tenants with:
- ArgoCD (Akuity SaaS)
- Kong API Gateway
- External Secrets Operator
- Datadog
- cert-manager
- Azure Entra ID
- Crossplane

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-04  
**Maintainer**: Platform Engineering Team
