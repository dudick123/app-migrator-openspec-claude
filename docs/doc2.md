# ArgoCD Migration Guide for Tenants

## What's Happening?

We are migrating our ArgoCD deployment platform from a self-managed (OSS) installation to Akuity's managed SaaS platform. This migration will provide improved reliability, enhanced features, and reduced operational overhead while maintaining the GitOps workflows you're familiar with.

**Your applications and deployments will not be affected during this migration.** We've designed a zero-downtime migration process that ensures your workloads continue running without interruption.

## Why Are We Migrating?

- **Improved Reliability**: Akuity SaaS provides enterprise-grade availability and support
- **Enhanced Features**: Access to advanced deployment strategies and improved UI
- **Better Observability**: Enhanced insights into application health and sync status
- **Reduced Maintenance**: Platform team can focus on enabling your success rather than managing infrastructure

## Migration Approach

We use a **shadow-then-cutover** approach to ensure a safe migration:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Shadow Mode    │────▶│  Verification   │────▶│    Cutover      │
│  (You Review)   │     │  (You Approve)  │     │  (We Execute)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Shadow Migration**: We copy your application definitions to the new SaaS platform with sync disabled
2. **Verification**: You review your applications in the new platform to confirm everything looks correct
3. **Cutover**: Once you approve, we switch which control plane is actively syncing your applications

## Migration Timeline

Migrations proceed environment by environment across successive sprints:

| Environment | Sprint | When to Expect Communication |
|-------------|--------|------------------------------|
| Dev | Sprint N | 1 week before sprint starts |
| NonProd | Sprint N+1 | 1 week before sprint starts |
| Prod | Sprint N+2 | 1 week before sprint starts |

Within each sprint:
- **Week 1**: Preparation and scheduling
- **Week 2**: Shadow migration, your verification, and cutover

You will receive specific dates for your tenant via email/Teams.

## Your Responsibilities

### Before Migration

- [ ] Confirm your tenant contact information is current
- [ ] Ensure team members who need SaaS ArgoCD access are identified
- [ ] Review the verification checklist (provided separately)
- [ ] Identify any critical deployment windows to avoid during cutover

### During Shadow Period

- [ ] Log into the SaaS ArgoCD console when notified
- [ ] Review your applications and verify they appear correct
- [ ] Compare with your current OSS ArgoCD applications
- [ ] Report any discrepancies to the Platform Team
- [ ] Provide written sign-off when satisfied

### During Cutover

- [ ] Avoid triggering deployments during the cutover window (typically 30 minutes)
- [ ] Be available for questions if issues arise
- [ ] Verify your applications after cutover notification

### After Cutover

- [ ] Use the new SaaS ArgoCD console for all operations
- [ ] Update any bookmarks or documentation
- [ ] Report any issues immediately

## What You Need to Verify

When reviewing your applications in SaaS ArgoCD shadow mode:

1. **Application List**: All your applications appear in the SaaS console
2. **Configuration**: Application settings match your expectations
3. **Repository Access**: Applications show they can reach your Git repositories
4. **Target Clusters**: Applications are targeting the correct clusters/namespaces
5. **Health Status**: Applications show expected health status (may show "Unknown" for sync status in shadow mode—this is expected)

**Note**: Applications will show as "Out of Sync" in shadow mode because sync is intentionally disabled. This is expected behavior.

## Accessing SaaS ArgoCD

You will receive access instructions when your migration is scheduled. Key differences from OSS:

| Aspect | OSS ArgoCD | SaaS ArgoCD |
|--------|------------|-------------|
| URL | [Current OSS URL] | [New SaaS URL - TBD] |
| Authentication | [Current Auth] | SSO via Azure AD |
| Your Projects | Same project names | Same project names |

Your RBAC permissions will be equivalent to what you have today.

## What Stays the Same

- **Your Git repositories**: No changes needed to your GitOps repos
- **Your deployment process**: Continue pushing to Git as usual
- **Your application names**: All naming conventions preserved
- **Your project structure**: ArgoCD projects remain the same
- **Your sync policies**: All policies migrated as-is

## What Changes

- **ArgoCD Console URL**: You'll use a new URL to access the ArgoCD UI
- **UI Appearance**: Akuity SaaS has an updated interface (same concepts, modern look)
- **Authentication**: SSO login experience may differ slightly

## Frequently Asked Questions

### Will my deployments be affected?

No. Your running workloads are not touched during migration. We're only changing which ArgoCD instance manages the sync process.

### What if something goes wrong?

We maintain the ability to roll back to the OSS ArgoCD instance for 48 hours after cutover. If issues arise, we can quickly revert.

### Do I need to update my Git repositories?

No. Your GitOps repositories remain unchanged. ArgoCD will continue pulling from the same repos.

### How long will the cutover take?

The actual cutover takes approximately 5-10 minutes. You may want to avoid deployments during this window.

### Can I request a specific cutover time?

Yes. Contact your Platform Team liaison to discuss scheduling preferences, especially if you have critical deployment windows to avoid.

### What if I find issues during verification?

Report them immediately to the Platform Team. We will investigate and resolve before proceeding to cutover. Your sign-off is required before we proceed.

### Will my CI/CD pipelines be affected?

If your pipelines interact directly with the ArgoCD API (e.g., to trigger syncs or check status), you may need to update the API endpoint after cutover. We will coordinate with you on this.

## Support and Contacts

| Role | Contact | When to Reach Out |
|------|---------|-------------------|
| Your Tenant Liaison | [TBD per tenant] | Questions, scheduling, verification help |
| Platform Team | [Team Channel/Email] | Technical issues, urgent problems |
| Migration Lead | [TBD] | Escalations, schedule conflicts |

## Providing Feedback

After your migration is complete, we'll send a brief survey to understand your experience. Your feedback helps us improve the process for remaining tenants.

---

**Questions?** Reach out to your Tenant Liaison or post in [Platform Team Channel].