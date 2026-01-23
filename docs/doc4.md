# Platform Team Migration Checklist

## Instructions

Complete this checklist for each tenant migration. Check items as completed and document any issues or notes in the provided spaces.

---

## Tenant Information

| Field | Value |
|-------|-------|
| **Tenant Name** | |
| **Environment** | ☐ Dev  ☐ NonProd  ☐ Prod |
| **Number of Applications** | |
| **Migration Batch** | |
| **Assigned Migration Executor** | |
| **Assigned Auditor** | |
| **Tenant Liaison** | |
| **Tenant Primary Contact** | |
| **Shadow Migration Date** | |
| **Planned Cutover Date** | |

---

## Pre-Migration Checklist

*Complete before shadow migration begins*

### Environment Readiness

- [ ] SaaS ArgoCD instance is healthy and accessible
- [ ] Tenant's ArgoCD Project exists in SaaS
- [ ] RBAC configured for tenant in SaaS
- [ ] Repository credentials available in SaaS (External Secrets synced)
- [ ] Cluster credentials configured in SaaS
- [ ] Network connectivity verified (SaaS → target cluster)

### Tenant Inventory

- [ ] All tenant applications inventoried from OSS
- [ ] Application count: ___________
- [ ] Special configurations documented (sync windows, custom health checks, etc.)
- [ ] ApplicationSets identified: ___________
- [ ] Webhook configurations noted

### Communication

- [ ] Tenant notified of shadow migration date
- [ ] Tenant contact information confirmed
- [ ] Verification window scheduled with tenant
- [ ] Cutover preferences collected (time of day, blackout periods)

### Pre-Migration Notes

```
[Document any tenant-specific considerations, special configurations, or concerns]




```

---

## Shadow Migration Checklist

*Complete during shadow migration execution*

### Migration Execution

- [ ] Migration script/tooling prepared
- [ ] Dry run completed successfully
- [ ] Shadow migration executed
- [ ] Start time: ___________
- [ ] End time: ___________

### Post-Migration Verification

- [ ] All applications visible in SaaS ArgoCD console
- [ ] Application count matches inventory: _____ / _____
- [ ] Applications show `syncPolicy: null` (sync disabled)
- [ ] Applications can connect to Git repositories
- [ ] Applications show target cluster connectivity
- [ ] No error states in application list

### Application Status Check

| Application Name | Visible in SaaS | Repo Connected | Cluster Connected | Health Status | Notes |
|------------------|-----------------|----------------|-------------------|---------------|-------|
| | ☐ | ☐ | ☐ | | |
| | ☐ | ☐ | ☐ | | |
| | ☐ | ☐ | ☐ | | |
| | ☐ | ☐ | ☐ | | |
| | ☐ | ☐ | ☐ | | |
| | ☐ | ☐ | ☐ | | |
| | ☐ | ☐ | ☐ | | |
| | ☐ | ☐ | ☐ | | |

*Add rows as needed*

### Shadow Migration Issues

```
[Document any issues encountered during shadow migration]




```

---

## Platform Audit Checklist

*Complete after shadow migration, before tenant verification*

### Configuration Parity Check

For each application, verify:

- [ ] `spec.source` matches (repo URL, path, targetRevision)
- [ ] `spec.destination` matches (server, namespace)
- [ ] `spec.project` matches
- [ ] `spec.syncPolicy` is null (intentionally disabled)
- [ ] Original syncPolicy documented for restoration at cutover
- [ ] `spec.ignoreDifferences` matches
- [ ] `spec.info` and annotations preserved
- [ ] Labels preserved

### Manifest Comparison

- [ ] Manual diff triggered in SaaS for each application
- [ ] Rendered manifests compared between OSS and SaaS
- [ ] Discrepancies documented and explained

### Discrepancies Found

| Application | Discrepancy | Root Cause | Resolution |
|-------------|-------------|------------|------------|
| | | | |
| | | | |
| | | | |

### Audit Sign-Off

- [ ] All applications audited
- [ ] No blocking issues identified
- [ ] Auditor sign-off obtained

**Auditor**: _____________________ **Date**: ___________

### Audit Notes

```
[Document audit findings, recommendations, or concerns]




```

---

## Tenant Verification Checklist

*Track tenant verification progress*

### Verification Request

- [ ] Tenant notified that applications are ready for verification
- [ ] SaaS access instructions provided
- [ ] Verification checklist shared with tenant
- [ ] Verification deadline communicated: ___________

### Verification Tracking

- [ ] Tenant logged into SaaS ArgoCD
- [ ] Tenant reviewed application list
- [ ] Tenant questions addressed
- [ ] Tenant concerns resolved

### Tenant Feedback

```
[Document any feedback, questions, or concerns from tenant]




```

### Tenant Sign-Off

- [ ] **Written tenant approval received**
- [ ] Approval method: ☐ Email  ☐ Ticket  ☐ Teams/Slack  ☐ Other: ________
- [ ] Approval reference: ___________
- [ ] Approval date: ___________
- [ ] Approver name: ___________

---

## Cutover Checklist

*Complete during cutover execution*

### Pre-Cutover Verification

- [ ] Tenant sign-off confirmed
- [ ] No active deployments in progress for tenant
- [ ] Cutover window communicated to tenant
- [ ] Rollback procedure reviewed
- [ ] On-call/escalation contacts available
- [ ] Datadog dashboards open for monitoring

### Cutover Execution

**Cutover Start Time**: ___________

#### Step 1: Disable Sync in OSS

- [ ] Set `syncPolicy: null` for all tenant applications in OSS
- [ ] Verify no sync operations are in progress
- [ ] Applications show "Synced" (not actively syncing)
- [ ] Time completed: ___________

#### Step 2: Wait Period

- [ ] Wait 5 minutes for any in-flight operations to complete
- [ ] Verify cluster state is stable
- [ ] Time completed: ___________

#### Step 3: Enable Sync in SaaS

- [ ] Restore original `syncPolicy` for all tenant applications in SaaS
- [ ] Time completed: ___________

#### Step 4: Trigger Initial Sync

- [ ] Trigger manual sync for each application
- [ ] Time completed: ___________

#### Step 5: Verify Sync Success

- [ ] All applications show "Synced" status
- [ ] All applications show "Healthy" status
- [ ] No unexpected resource changes detected
- [ ] Time completed: ___________

**Cutover End Time**: ___________

**Total Cutover Duration**: ___________

### Post-Cutover Application Status

| Application Name | Sync Status | Health Status | Notes |
|------------------|-------------|---------------|-------|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

### Post-Cutover Verification

- [ ] Tenant notified of successful cutover
- [ ] Tenant verified applications from their side
- [ ] No deployment issues reported
- [ ] Datadog metrics normal
- [ ] 1-hour post-cutover check completed

### Cutover Issues

```
[Document any issues encountered during cutover]




```

---

## Stabilization Period Checklist

*Complete during 48-hour stabilization period*

### Monitoring

- [ ] 4-hour check completed - Time: ___________
- [ ] 12-hour check completed - Time: ___________
- [ ] 24-hour check completed - Time: ___________
- [ ] 48-hour check completed - Time: ___________

### Issues During Stabilization

| Time | Issue | Resolution | Rollback Required? |
|------|-------|------------|-------------------|
| | | | ☐ Yes  ☐ No |
| | | | ☐ Yes  ☐ No |

### Stabilization Complete

- [ ] 48-hour period completed without critical issues
- [ ] Tenant confirms no issues
- [ ] Ready to archive OSS applications

---

## OSS Cleanup Checklist

*Complete after stabilization period*

- [ ] OSS applications archived (not deleted)
- [ ] Archive location documented: ___________
- [ ] Archive date: ___________
- [ ] Verified SaaS is sole active control plane

---

## Migration Complete

### Summary

| Metric | Value |
|--------|-------|
| Total applications migrated | |
| Shadow migration duration | |
| Cutover duration | |
| Issues encountered | |
| Rollbacks required | |

### Final Sign-Off

**Migration Executor**: _____________________ **Date**: ___________

**Migration Lead**: _____________________ **Date**: ___________

### Lessons Learned

```
[Document any lessons learned or recommendations for future migrations]




```

---

## Rollback Record

*Complete only if rollback was required*

### Rollback Decision

- [ ] Rollback authorized by: ___________
- [ ] Rollback reason: ___________
- [ ] Rollback time: ___________

### Rollback Execution

- [ ] Sync disabled in SaaS ArgoCD
- [ ] Sync re-enabled in OSS ArgoCD
- [ ] Applications syncing successfully in OSS
- [ ] Tenant notified of rollback

### Post-Rollback

- [ ] Root cause investigation initiated
- [ ] Issue ticket created: ___________
- [ ] Re-migration scheduled for: ___________