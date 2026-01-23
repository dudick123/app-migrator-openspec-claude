# ArgoCD OSS to SaaS Migration: Platform Team Process Guide

## Overview

This document outlines the process for migrating tenants from our self-managed ArgoCD (OSS) to Akuity SaaS ArgoCD. The migration follows a phased approach across environments with rolling tenant migrations within each phase.

## Migration Philosophy

The migration uses a **shadow-then-cutover** approach to minimize risk and ensure zero downtime for tenant workloads:

1. Applications are first migrated to SaaS in **shadow mode** (sync disabled)
2. Both control planes run in parallel during validation
3. Cutover happens only after tenant verification
4. Rollback remains possible until OSS applications are archived

## Environment Migration Schedule

| Sprint | Environment | Shadow Migration Begins | Cutover Window |
|--------|-------------|------------------------|----------------|
| Sprint N | Dev | Week 2 | Week 2-3 |
| Sprint N+1 | NonProd | Week 2 | Week 2-3 |
| Sprint N+2 | Prod | Week 2 | Week 2-3 |

## Roles and Responsibilities

### Migration Lead

- Owns the overall migration timeline and communicates status to stakeholders
- Coordinates tenant scheduling and resolves conflicts
- Escalation point for issues during migration
- Signs off on environment completion before proceeding to next phase

### Platform Engineer (Migration Executor)

- Executes the technical migration of ArgoCD applications
- Performs pre-migration validation and post-migration audits
- Monitors both control planes during shadow period
- Executes cutover procedures
- Documents any tenant-specific configurations or issues

### Platform Engineer (Audit Role)

- Reviews migrated applications for configuration parity
- Validates sync policies, health checks, and resource configurations
- Confirms application manifests render identically in both control planes
- Signs off on tenant readiness for cutover

### Tenant Liaison

- Primary point of contact for assigned tenants
- Communicates migration schedule and expectations
- Guides tenants through verification process
- Collects tenant sign-off before cutover

## Migration Process

### Phase 1: Pre-Migration Preparation (Week 1)

1. **Tenant Communication**
   - Send migration schedule notification to all tenants in the target environment
   - Confirm tenant contacts and escalation paths
   - Schedule verification windows with tenants

2. **Environment Validation**
   - Verify SaaS ArgoCD instance is healthy and accessible
   - Confirm RBAC policies are configured for target tenants
   - Validate network connectivity between SaaS control plane and clusters
   - Test repository credentials and secrets synchronization

3. **Tenant Inventory**
   - Document all applications per tenant in OSS ArgoCD
   - Note any custom configurations, plugins, or sync windows
   - Identify applications with special handling requirements

### Phase 2: Shadow Migration (Week 2, Days 1-2)

1. **Execute Migration Script**
   - Run migration tooling to create SaaS applications from OSS definitions
   - Applications are created with `syncPolicy: null` (manual sync disabled)
   - Preserve all application metadata, labels, and annotations

2. **Initial Validation**
   - Verify applications appear in SaaS ArgoCD console
   - Confirm applications can connect to target clusters
   - Validate repository access and manifest rendering

3. **Document Migration**
   - Record migration timestamp per application
   - Note any errors or warnings during migration
   - Update tenant tracking spreadsheet

### Phase 3: Platform Audit (Week 2, Days 2-3)

1. **Configuration Parity Check**
   - Compare application specs between OSS and SaaS
   - Verify sync policies match (accounting for intentional shadow mode difference)
   - Confirm health assessment configurations are identical
   - Validate ignore differences and sync options

2. **Manifest Comparison**
   - Trigger manual diff in SaaS ArgoCD
   - Compare rendered manifests with OSS control plane
   - Document any discrepancies and root cause

3. **Audit Sign-Off**
   - Complete audit checklist for each tenant
   - Flag any applications requiring additional attention
   - Notify tenant liaison that verification can begin

### Phase 4: Tenant Verification (Week 2, Days 3-4)

1. **Tenant Notification**
   - Inform tenant their applications are ready for review in SaaS
   - Provide SaaS ArgoCD access instructions
   - Share verification checklist with tenant

2. **Support Tenant Review**
   - Be available for tenant questions during verification window
   - Assist with navigation of SaaS ArgoCD interface
   - Address any concerns or discrepancies identified

3. **Collect Sign-Off**
   - Obtain written confirmation from tenant (email or ticket)
   - Document any conditional approvals or noted concerns
   - Update tracking to mark tenant as verified

### Phase 5: Cutover (Week 2-3)

1. **Pre-Cutover Checklist**
   - Confirm tenant sign-off received
   - Verify no active deployments in progress for tenant
   - Confirm rollback procedure is documented and tested
   - Notify tenant of cutover time window

2. **Execute Cutover**
   - **Step 1:** Disable sync in OSS ArgoCD (set `syncPolicy: null`)
   - **Step 2:** Wait for any in-progress syncs to complete (max 5 minutes)
   - **Step 3:** Enable sync in SaaS ArgoCD (restore original `syncPolicy`)
   - **Step 4:** Trigger manual sync to verify functionality
   - **Step 5:** Monitor for successful sync and healthy status

3. **Post-Cutover Validation**
   - Confirm application shows "Synced" and "Healthy" in SaaS
   - Verify no drift detected in target cluster
   - Check Datadog dashboards for any anomalies
   - Notify tenant of successful cutover

4. **OSS Cleanup (After Stabilization)**
   - After 48-hour stabilization period, archive OSS applications
   - Do not delete immediately—maintain for rollback capability
   - Full OSS decommission occurs after all environments complete

## Rollback Procedure

If issues are detected post-cutover:

1. **Immediate Rollback (Within 48 hours)**
   - Disable sync in SaaS ArgoCD
   - Re-enable sync in OSS ArgoCD
   - Notify tenant of rollback
   - Document issue for investigation

2. **Investigation**
   - Determine root cause of failure
   - Implement fix in SaaS configuration
   - Schedule re-migration with tenant

## Communication Templates

### Tenant Migration Notification

```
Subject: ArgoCD Migration Scheduled - [Environment] - [Date Range]

Your applications in [Environment] are scheduled for migration to our new 
ArgoCD SaaS platform. Please review the attached schedule and verification 
checklist.
```

### Tenant Verification Request

```
Subject: Action Required: Verify ArgoCD Applications in SaaS

Your applications have been migrated to shadow mode in ArgoCD SaaS. Please 
verify your applications by [Date] and confirm readiness for cutover.
```

### Cutover Notification

```
Subject: ArgoCD Cutover Complete - [Environment]

Your applications have been successfully cut over to ArgoCD SaaS. Please 
verify your applications are syncing correctly.
```

## Escalation Path

| Issue Type | First Contact | Escalation |
|------------|---------------|------------|
| Migration script failure | Migration Executor | Migration Lead |
| Tenant verification concerns | Tenant Liaison | Migration Lead |
| Post-cutover sync issues | Migration Executor | Migration Lead → On-call |
| Rollback decision | Migration Lead | Platform Team Lead |

## Success Criteria

A tenant migration is considered complete when:

- [ ] All applications migrated to SaaS and validated
- [ ] Platform audit completed with no blocking issues
- [ ] Tenant verification received (written sign-off)
- [ ] Cutover executed successfully
- [ ] 48-hour stabilization period passed with no issues
- [ ] OSS applications archived

## Metrics and Reporting

Track the following metrics throughout migration:

- Number of tenants migrated per sprint
- Average time from shadow migration to cutover
- Number of rollbacks required
- Tenant satisfaction (post-migration survey)
- Issues encountered and resolution time