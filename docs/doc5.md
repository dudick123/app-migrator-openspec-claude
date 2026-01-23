# Tenant Migration Verification Checklist

## Your Migration Details

| Field | Value |
|-------|-------|
| **Tenant Name** | |
| **Environment** | ☐ Dev  ☐ NonProd  ☐ Prod |
| **Shadow Migration Date** | |
| **Verification Due Date** | |
| **Planned Cutover Date** | |
| **Your Platform Team Contact** | |

---

## Before Migration

*Complete these items before your shadow migration date*

### Preparation

- [ ] Confirmed your team's contact information with Platform Team
- [ ] Identified team members who need SaaS ArgoCD access
- [ ] Reviewed this checklist
- [ ] Noted any deployment freezes or critical windows to avoid

### Access Verification

- [ ] Received SaaS ArgoCD URL: ___________________________
- [ ] Tested SSO login to SaaS ArgoCD
- [ ] Can see your ArgoCD Project in the new console

### Questions or Concerns

```
[Note any questions to discuss with Platform Team before migration]




```

---

## Shadow Migration Verification

*Complete these items after you receive notification that shadow migration is complete*

### Application Inventory

**Expected number of applications**: _______

- [ ] All expected applications are visible in SaaS ArgoCD
- [ ] Actual count matches expected: _______ / _______

List any missing applications:

| Missing Application Name | Notes |
|--------------------------|-------|
| | |
| | |

### Application Configuration Review

For each of your applications, verify the following appears correct:

#### Application 1: ________________________

- [ ] Application name is correct
- [ ] Git repository URL is correct
- [ ] Git branch/revision is correct
- [ ] Path within repository is correct
- [ ] Target cluster is correct
- [ ] Target namespace is correct
- [ ] Sync status shows "OutOfSync" or "Unknown" (expected in shadow mode)
- [ ] Health status appears reasonable

Notes: _________________________________________________________________

#### Application 2: ________________________

- [ ] Application name is correct
- [ ] Git repository URL is correct
- [ ] Git branch/revision is correct
- [ ] Path within repository is correct
- [ ] Target cluster is correct
- [ ] Target namespace is correct
- [ ] Sync status shows "OutOfSync" or "Unknown" (expected in shadow mode)
- [ ] Health status appears reasonable

Notes: _________________________________________________________________

#### Application 3: ________________________

- [ ] Application name is correct
- [ ] Git repository URL is correct
- [ ] Git branch/revision is correct
- [ ] Path within repository is correct
- [ ] Target cluster is correct
- [ ] Target namespace is correct
- [ ] Sync status shows "OutOfSync" or "Unknown" (expected in shadow mode)
- [ ] Health status appears reasonable

Notes: _________________________________________________________________

#### Application 4: ________________________

- [ ] Application name is correct
- [ ] Git repository URL is correct
- [ ] Git branch/revision is correct
- [ ] Path within repository is correct
- [ ] Target cluster is correct
- [ ] Target namespace is correct
- [ ] Sync status shows "OutOfSync" or "Unknown" (expected in shadow mode)
- [ ] Health status appears reasonable

Notes: _________________________________________________________________

*Copy this section for additional applications as needed*

### What to Expect in Shadow Mode

**Normal/Expected:**
- Sync Status: "OutOfSync" or "Unknown" — This is expected because sync is disabled
- Health Status: Should reflect actual application health
- Diff View: May show differences if your apps have drifted

**Concerning (Report These):**
- Application shows error connecting to repository
- Application shows error connecting to cluster
- Application name, repo, or destination is wrong
- Application is completely missing

### Discrepancies Found

| Application | Issue Found | Reported To | Resolution |
|-------------|-------------|-------------|------------|
| | | | |
| | | | |
| | | | |

---

## Sign-Off

### Verification Complete

- [ ] I have reviewed all applications listed above
- [ ] All applications appear correctly configured
- [ ] I have reported any discrepancies to the Platform Team
- [ ] All reported issues have been resolved
- [ ] **I approve proceeding with cutover**

### Sign-Off Details

| Field | Value |
|-------|-------|
| **Your Name** | |
| **Your Email** | |
| **Date** | |
| **Preferred Cutover Window** | ☐ Morning  ☐ Afternoon  ☐ No Preference |
| **Times to Avoid** | |

### How to Submit Sign-Off

Provide your sign-off by one of the following methods:

1. **Email**: Reply to the verification notification email with "Approved" and this completed checklist
2. **Ticket**: Update the migration ticket with your approval
3. **Teams/Slack**: Message your Platform Team contact with confirmation

**Note**: We cannot proceed with cutover until written sign-off is received.

---

## During Cutover

*Your responsibilities during the cutover window*

### Before Cutover

- [ ] Received notification that cutover is starting
- [ ] Paused any planned deployments
- [ ] Available via Teams/Slack/email for questions

### Cutover Window (Approximately 15-30 minutes)

During this time:
- **Do not** trigger any deployments to affected applications
- **Do not** make changes to Git repositories that would trigger syncs
- **Do** remain available in case Platform Team has questions

### After Cutover

You will receive a notification when cutover is complete.

- [ ] Received cutover complete notification
- [ ] Logged into SaaS ArgoCD
- [ ] Verified applications show "Synced" status
- [ ] Verified applications show "Healthy" status
- [ ] Confirmed no unexpected changes to your workloads

---

## Post-Migration Checklist

*Complete these items after successful cutover*

### Immediate (Day 1)

- [ ] Updated bookmarks to new SaaS ArgoCD URL
- [ ] Verified can trigger manual sync successfully
- [ ] Tested a low-risk deployment through GitOps workflow
- [ ] No issues reported by end users

### First Week

- [ ] All team members can access SaaS ArgoCD
- [ ] Normal deployment cadence resumed
- [ ] Any CI/CD integrations updated (if applicable)
- [ ] Documentation/runbooks updated with new URLs
- [ ] Completed post-migration survey (when received)

### Issues After Cutover

If you experience any issues after cutover:

1. **Immediate**: Contact Platform Team via [urgent channel]
2. **Non-urgent**: Submit a ticket to [ticketing system]

We maintain rollback capability for 48 hours after cutover.

---

## Quick Reference

### Key URLs

| System | URL |
|--------|-----|
| SaaS ArgoCD | |
| Old OSS ArgoCD (view only after cutover) | |
| Platform Team Support Channel | |
| Migration Documentation | |

### Key Contacts

| Role | Name | Contact |
|------|------|---------|
| Your Tenant Liaison | | |
| Platform Team Channel | | |
| Emergency Escalation | | |

### Timeline Reminder

```
Shadow Migration → 24-48 hrs → Your Verification → Sign-Off → Cutover → 48 hrs → Complete
        ↓                            ↓                            ↓
   You receive              Review apps in              Continue using
   notification              SaaS ArgoCD                 SaaS ArgoCD
```

---

## Feedback

After your migration is complete, please share your experience:

**What went well?**
```




```

**What could be improved?**
```




```

**Any other comments?**
```




```

Thank you for your partnership in this migration!
