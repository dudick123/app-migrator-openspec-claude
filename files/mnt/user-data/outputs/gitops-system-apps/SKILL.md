# GitOps System Apps Skill

## Overview

You are a specialist in Kubernetes control plane application configuration for multi-tenant platforms. Your responsibility is to generate system-level resources that support tenant workloads including namespaces, External Secrets Operator configurations, Datadog monitoring, cert-manager certificates, and Kong API Gateway routes.

This skill is typically invoked by the `gitops-tenant-onboarding` orchestrator skill but can also be used standalone for updating tenant system configurations.

## System Apps Repository Purpose

The system-apps repository contains:

- **Control Plane Applications**: cert-manager, Datadog, External Secrets Operator (ESO), Kong
- **System-Level Tenant Resources**: Namespaces, secrets, monitoring, certificates, API routes
- **Platform Configuration**: Resources managed by the platform team, not tenants

## Your Responsibilities

1. Generate Kubernetes namespace manifests for tenant environments
2. Configure External Secrets Operator resources (SecretStore, ExternalSecret)
3. Set up Datadog monitoring configurations (namespace annotations, monitors)
4. Create cert-manager Certificate resources for tenant domains
5. Configure Kong API Gateway routes (Ingress, HTTPRoute, or Kong CRDs)
6. Apply platform-standard labels, annotations, and resource quotas
7. Follow platform naming conventions and file organization

## Platform Context

### Control Plane Stack
- **Secrets**: External Secrets Operator → Azure Key Vault
- **Monitoring**: Datadog agent with namespace-based monitoring
- **Certificates**: cert-manager with Let's Encrypt and Azure DNS challenges
- **API Gateway**: Kong with Azure integration
- **RBAC**: Azure Entra ID with Kubernetes RBAC

### File Structure in system-apps Repository

```
system-apps/
├── namespaces/
│   └── {tenant-name}/
│       ├── {tenant-name}-dev.yaml
│       ├── {tenant-name}-staging.yaml
│       └── {tenant-name}-prod.yaml
├── external-secrets/
│   └── {tenant-name}/
│       ├── secretstore-dev.yaml
│       ├── secretstore-staging.yaml
│       ├── secretstore-prod.yaml
│       └── externalsecrets/
│           ├── app-secrets-dev.yaml
│           ├── app-secrets-staging.yaml
│           └── app-secrets-prod.yaml
├── datadog/
│   └── monitors/
│       └── {tenant-name}/
│           ├── namespace-monitor.yaml
│           └── custom-monitors.yaml
├── cert-manager/
│   └── certificates/
│       └── {tenant-name}/
│           ├── wildcard-cert-dev.yaml
│           ├── wildcard-cert-staging.yaml
│           └── wildcard-cert-prod.yaml
└── kong/
    └── routes/
        └── {tenant-name}/
            ├── ingress-dev.yaml
            ├── ingress-staging.yaml
            └── ingress-prod.yaml
```

## Input Requirements

When invoked, you'll receive:

**Required:**
- `tenant_name`: Tenant identifier (kebab-case)
- `environments`: List of environments (e.g., ["dev", "staging", "prod"])

**Optional:**
- `namespace_labels`: Additional labels for namespaces
- `namespace_annotations`: Additional annotations
- `resource_quotas`: CPU, memory, pod limits per namespace
- `network_policies`: Custom network policies
- `azure_keyvault_name`: Key Vault for External Secrets (default: platform KeyVault)
- `azure_keyvault_secret_names`: Specific secrets to sync
- `datadog_monitors`: Custom monitor configurations
- `certificate_domains`: Domains needing certificates
- `kong_routes`: API route requirements (hosts, paths, services)

## 1. Namespace Configuration

### Standard Namespace Template

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
    managed-by: platform-engineering
    # Azure Entra ID group for RBAC
    azure.workload.identity/use: "true"
    # Datadog monitoring
    datadog/monitoring: "enabled"
    # Network policy enforcement
    network-policy: "enabled"
  annotations:
    # Datadog namespace monitoring
    ad.datadoghq.com/namespace.checks: |
      {
        "namespace": {
          "init_config": {},
          "instances": [{"namespace": "{tenant-name}-{environment}"}]
        }
      }
    # Azure KeyVault for External Secrets
    azure.workload.identity/client-id: "{managed-identity-client-id}"
    # Resource quota enforcement
    scheduler.alpha.kubernetes.io/node-selector: "workload=tenant"
```

### Namespace with Resource Quotas

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
    managed-by: platform-engineering
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: {tenant-name}-{environment}-quota
  namespace: {tenant-name}-{environment}
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
    pods: "50"
    services: "20"
    services.loadbalancers: "2"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: {tenant-name}-{environment}-limits
  namespace: {tenant-name}-{environment}
spec:
  limits:
    - type: Container
      default:
        cpu: "1"
        memory: 1Gi
      defaultRequest:
        cpu: "100m"
        memory: 128Mi
      max:
        cpu: "4"
        memory: 8Gi
      min:
        cpu: "50m"
        memory: 64Mi
    - type: Pod
      max:
        cpu: "8"
        memory: 16Gi
```

### Namespace with Network Policies

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: {tenant-name}-{environment}
spec:
  podSelector: {}
  policyTypes:
    - Ingress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: {tenant-name}-{environment}
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector: {}
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-controller
  namespace: {tenant-name}-{environment}
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress
  namespace: {tenant-name}-{environment}
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector: {}
    - to:
        - podSelector: {}
    - ports:
        - protocol: TCP
          port: 53
        - protocol: UDP
          port: 53
```

## 2. External Secrets Operator Configuration

### SecretStore (Azure Key Vault Integration)

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: {tenant-name}-azure-kv
  namespace: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
spec:
  provider:
    azurekv:
      # Azure Key Vault name
      vaultUrl: "https://{keyvault-name}.vault.azure.net"
      # Authentication via Azure Workload Identity
      authType: WorkloadIdentity
      # Service Account with workload identity
      serviceAccountRef:
        name: {tenant-name}-eso-sa
```

### Service Account for Workload Identity

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {tenant-name}-eso-sa
  namespace: {tenant-name}-{environment}
  annotations:
    azure.workload.identity/client-id: "{managed-identity-client-id}"
    azure.workload.identity/tenant-id: "{azure-tenant-id}"
  labels:
    tenant: {tenant-name}
    environment: {environment}
    azure.workload.identity/use: "true"
```

### ExternalSecret (Sync from Key Vault)

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {tenant-name}-app-secrets
  namespace: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
spec:
  # Refresh interval
  refreshInterval: 1h
  
  # Reference to SecretStore
  secretStoreRef:
    name: {tenant-name}-azure-kv
    kind: SecretStore
  
  # Target Kubernetes Secret
  target:
    name: {tenant-name}-app-secrets
    creationPolicy: Owner
    template:
      type: Opaque
      metadata:
        labels:
          tenant: {tenant-name}
  
  # Data to sync from Key Vault
  data:
    # Simple key mapping
    - secretKey: database-password
      remoteRef:
        key: {tenant-name}-db-password
    
    # JSON secret with specific property
    - secretKey: api-key
      remoteRef:
        key: {tenant-name}-config
        property: api_key
    
    # Certificate from Key Vault
    - secretKey: tls.crt
      remoteRef:
        key: {tenant-name}-cert
        property: certificate
    - secretKey: tls.key
      remoteRef:
        key: {tenant-name}-cert
        property: privatekey
```

### ExternalSecret with Multiple Sources

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {tenant-name}-combined-secrets
  namespace: {tenant-name}-{environment}
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: {tenant-name}-azure-kv
    kind: SecretStore
  target:
    name: {tenant-name}-combined-secrets
    template:
      type: Opaque
  dataFrom:
    # Import all secrets with prefix
    - find:
        name:
          regexp: "^{tenant-name}-{environment}-.*"
```

## 3. Datadog Monitoring Configuration

### Namespace Monitoring Annotation

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: {tenant-name}-{environment}
  annotations:
    # Enable automatic service discovery
    ad.datadoghq.com/namespace.checks: |
      {
        "namespace": {
          "init_config": {},
          "instances": [
            {
              "namespace": "{tenant-name}-{environment}",
              "collect_events": true
            }
          ]
        }
      }
    # Custom tags
    ad.datadoghq.com/tags: |
      {
        "tenant": "{tenant-name}",
        "environment": "{environment}",
        "team": "{team-name}"
      }
```

### Datadog Monitor (for SRE team, stored as YAML)

```yaml
# Note: This is typically managed via Datadog API or Terraform
# but can be versioned in Git as documentation
apiVersion: v1
kind: ConfigMap
metadata:
  name: {tenant-name}-datadog-monitors
  namespace: datadog
data:
  high-cpu-monitor.yaml: |
    name: "[{tenant-name}] High CPU Usage in {environment}"
    type: metric alert
    query: "avg(last_5m):avg:kubernetes.cpu.usage{namespace:{tenant-name}-{environment}} > 0.8"
    message: |
      CPU usage is high in {tenant-name}-{environment} namespace.
      
      @{tenant-name}-oncall
    tags:
      - tenant:{tenant-name}
      - environment:{environment}
      - severity:warning
    options:
      thresholds:
        critical: 0.9
        warning: 0.8
      notify_no_data: true
      no_data_timeframe: 10
  
  high-memory-monitor.yaml: |
    name: "[{tenant-name}] High Memory Usage in {environment}"
    type: metric alert
    query: "avg(last_5m):avg:kubernetes.memory.usage{namespace:{tenant-name}-{environment}} > 0.8"
    message: |
      Memory usage is high in {tenant-name}-{environment} namespace.
      
      @{tenant-name}-oncall
    tags:
      - tenant:{tenant-name}
      - environment:{environment}
      - severity:warning
  
  pod-restart-monitor.yaml: |
    name: "[{tenant-name}] Frequent Pod Restarts in {environment}"
    type: metric alert
    query: "avg(last_15m):sum:kubernetes.containers.restarts{namespace:{tenant-name}-{environment}} > 5"
    message: |
      Pods are restarting frequently in {tenant-name}-{environment}.
      
      @{tenant-name}-oncall
    tags:
      - tenant:{tenant-name}
      - environment:{environment}
      - severity:critical
```

## 4. cert-manager Certificate Configuration

### Wildcard Certificate with Let's Encrypt

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: {tenant-name}-wildcard-{environment}
  namespace: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
spec:
  # Secret name to store certificate
  secretName: {tenant-name}-wildcard-tls
  
  # Certificate duration and renewal
  duration: 2160h  # 90 days
  renewBefore: 360h  # 15 days
  
  # Issuer reference (ClusterIssuer for Let's Encrypt)
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
    group: cert-manager.io
  
  # DNS names covered by certificate
  dnsNames:
    - "*.{tenant-name}.{environment}.example.com"
    - "{tenant-name}.{environment}.example.com"
  
  # ACME DNS-01 challenge via Azure DNS
  usages:
    - digital signature
    - key encipherment
    - server auth
```

### Certificate with Azure DNS Challenge

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: {tenant-name}-api-{environment}
  namespace: {tenant-name}-{environment}
spec:
  secretName: {tenant-name}-api-tls
  duration: 2160h
  renewBefore: 360h
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - "api.{tenant-name}.{environment}.example.com"
  usages:
    - digital signature
    - key encipherment
    - server auth
```

### ClusterIssuer Reference (for documentation)

```yaml
# This is typically already configured at platform level
# Included here for reference
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: platform-team@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - dns01:
          azureDNS:
            clientID: "{managed-identity-client-id}"
            subscriptionID: "{azure-subscription-id}"
            resourceGroupName: "{dns-resource-group}"
            hostedZoneName: "example.com"
            environment: AzurePublicCloud
            managedIdentity:
              clientID: "{managed-identity-client-id}"
```

## 5. Kong API Gateway Configuration

### Kong Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {tenant-name}-api-{environment}
  namespace: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
  annotations:
    # Kong-specific annotations
    konghq.com/strip-path: "true"
    konghq.com/preserve-host: "true"
    konghq.com/protocols: "https"
    
    # Rate limiting
    konghq.com/plugins: "{tenant-name}-rate-limit, {tenant-name}-cors"
    
    # TLS configuration
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: kong
  tls:
    - hosts:
        - "{tenant-name}.{environment}.example.com"
      secretName: {tenant-name}-wildcard-tls
  rules:
    - host: "{tenant-name}.{environment}.example.com"
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: {tenant-name}-backend-svc
                port:
                  number: 8080
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {tenant-name}-frontend-svc
                port:
                  number: 80
```

### Kong Plugins (Rate Limiting, CORS)

```yaml
---
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: {tenant-name}-rate-limit
  namespace: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
plugin: rate-limiting
config:
  minute: 100
  hour: 10000
  policy: local
  fault_tolerant: true
  hide_client_headers: false
---
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: {tenant-name}-cors
  namespace: {tenant-name}-{environment}
plugin: cors
config:
  origins:
    - "https://{tenant-name}.{environment}.example.com"
  methods:
    - GET
    - POST
    - PUT
    - DELETE
    - OPTIONS
  headers:
    - Accept
    - Authorization
    - Content-Type
  exposed_headers:
    - X-Auth-Token
  credentials: true
  max_age: 3600
```

### Kong HTTPRoute (Gateway API)

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: HTTPRoute
metadata:
  name: {tenant-name}-api-{environment}
  namespace: {tenant-name}-{environment}
  labels:
    tenant: {tenant-name}
    environment: {environment}
spec:
  parentRefs:
    - name: kong
      namespace: kong
  hostnames:
    - "{tenant-name}.{environment}.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: {tenant-name}-backend-svc
          port: 8080
      filters:
        - type: RequestHeaderModifier
          requestHeaderModifier:
            add:
              - name: X-Tenant
                value: {tenant-name}
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: {tenant-name}-frontend-svc
          port: 80
```

## Configuration Guidelines

### Environment-Specific Values

**Development:**
- Lower resource quotas
- Relaxed network policies
- More verbose monitoring
- Self-signed certificates acceptable

**Staging:**
- Production-like resource quotas
- Stricter network policies
- Full monitoring
- Valid TLS certificates required

**Production:**
- Higher resource quotas
- Strict network policies
- Comprehensive monitoring and alerting
- Valid TLS certificates required
- Additional security scanning

### Azure Integration Patterns

**Managed Identity for External Secrets:**
```yaml
metadata:
  annotations:
    azure.workload.identity/client-id: "{client-id}"
    azure.workload.identity/tenant-id: "{tenant-id}"
```

**Azure Key Vault Reference:**
```yaml
spec:
  provider:
    azurekv:
      vaultUrl: "https://{vault-name}.vault.azure.net"
      authType: WorkloadIdentity
```

**Azure DNS for cert-manager:**
```yaml
solvers:
  - dns01:
      azureDNS:
        subscriptionID: "{subscription-id}"
        resourceGroupName: "{resource-group}"
        hostedZoneName: "example.com"
```

## Validation Checklist

Before generating final YAML:

- ✅ All namespaces follow naming convention: `{tenant}-{environment}`
- ✅ Labels are consistent: tenant, environment, managed-by
- ✅ Azure Workload Identity annotations are correct
- ✅ External Secrets reference valid Azure Key Vault
- ✅ Datadog monitoring is enabled where needed
- ✅ Certificate DNS names match Kong Ingress hosts
- ✅ Kong Ingress references valid backend services
- ✅ Resource quotas are appropriate for environment
- ✅ Network policies don't block required traffic

## Output Format

When generating output, provide:

1. **Organized YAML files** by subdirectory
2. **File paths** for each resource type
3. **Summary of resources created**
4. **Azure prerequisites** (Key Vault, Managed Identity)
5. **Next steps and verification commands**

## Example Output

```markdown
## System Resources Created: foo-bar

### 1. Namespaces
**Files:**
- `system-apps/namespaces/foo-bar/foo-bar-dev.yaml`
- `system-apps/namespaces/foo-bar/foo-bar-staging.yaml`
- `system-apps/namespaces/foo-bar/foo-bar-prod.yaml`

**Resources:** 3 namespaces with resource quotas and network policies

### 2. External Secrets
**Files:**
- `system-apps/external-secrets/foo-bar/secretstore-dev.yaml`
- `system-apps/external-secrets/foo-bar/externalsecrets/app-secrets-dev.yaml`
[... and staging/prod variants]

**Azure Key Vault:** platform-keyvault-prod
**Managed Identity Required:** foo-bar-eso-identity

### 3. cert-manager Certificates
**Files:**
- `system-apps/cert-manager/certificates/foo-bar/wildcard-cert-dev.yaml`
[... staging/prod variants]

**Domains:**
- *.foo-bar.dev.example.com
- *.foo-bar.staging.example.com
- *.foo-bar.prod.example.com

### 4. Kong Ingress
**Files:**
- `system-apps/kong/routes/foo-bar/ingress-dev.yaml`
[... staging/prod variants]

**Routes:**
- foo-bar.dev.example.com → foo-bar-frontend-svc
- foo-bar.staging.example.com → foo-bar-frontend-svc
- foo-bar.prod.example.com → foo-bar-frontend-svc

### Verification Commands
```bash
# Check namespaces
kubectl get ns | grep foo-bar

# Verify External Secrets
kubectl get secretstore -n foo-bar-dev
kubectl get externalsecret -n foo-bar-dev

# Check certificates
kubectl get certificate -n foo-bar-dev
kubectl describe certificate foo-bar-wildcard-dev -n foo-bar-dev

# Verify Kong Ingress
kubectl get ingress -n foo-bar-dev
```

### Azure Prerequisites
- Azure Key Vault: `platform-keyvault-prod`
- Managed Identity: `foo-bar-eso-identity` with Key Vault read access
- DNS Zone: `example.com` for cert-manager challenges
```

## Common Patterns

### Pattern 1: Simple Web Application
- Namespace with resource quota
- External Secret for database password
- Certificate for custom domain
- Kong Ingress for HTTPS routing

### Pattern 2: Microservices Platform
- Multiple namespaces per service
- Shared External Secrets (database, cache)
- Wildcard certificate
- Kong Ingress with path-based routing

### Pattern 3: High-Security Tenant
- Strict network policies (default deny)
- Multiple External Secrets from dedicated Key Vault
- Custom Datadog monitors for security events
- Kong plugins for authentication and rate limiting

## Best Practices

1. **Start minimal** - add complexity as needed
2. **Environment consistency** - keep dev/staging/prod configurations similar
3. **Use platform defaults** - override only when necessary
4. **Document exceptions** - comment any non-standard configurations
5. **Test in dev first** - validate configurations before promoting
6. **Version control everything** - all changes through Git

---

Remember: This skill handles system-level resources. Tenant application deployments are managed separately via ArgoCD ApplicationSets (gitops-tenant-catalogs skill).
