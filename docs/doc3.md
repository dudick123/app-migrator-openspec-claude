# ArgoCD Migration Planning Schedule

## Overview

This document provides the migration schedule for all tenants across Dev, NonProd, and Prod environments. Each tenant will receive notification of their specific shadow migration and cutover dates.

## Environment Migration Phases

```
Sprint N          Sprint N+1        Sprint N+2
┌──────────┐      ┌──────────┐      ┌──────────┐
│   DEV    │─────▶│ NONPROD  │─────▶│   PROD   │
│ Complete │      │ Complete │      │ Complete │
└──────────┘      └──────────┘      └──────────┘
```

## Sprint Schedule Template

Each sprint follows this pattern:

| Week | Day | Activity |
|------|-----|----------|
| Week 1 | Mon-Tue | Environment preparation and final tenant scheduling |
| Week 1 | Wed | Send tenant notifications with confirmed dates |
| Week 1 | Thu-Fri | Tenant Q&A, resolve scheduling conflicts |
| Week 2 | Mon | Shadow migrations begin (Batch 1) |
| Week 2 | Tue | Platform audit of Batch 1; Shadow migrations (Batch 2) |
| Week 2 | Wed | Tenant verification (Batch 1); Platform audit (Batch 2) |
| Week 2 | Thu | Cutover (Batch 1); Tenant verification (Batch 2) |
| Week 2 | Fri | Cutover (Batch 2); Begin stabilization monitoring |
| Week 3 | Mon-Tue | Complete any remaining cutovers; stabilization |
| Week 3 | Wed | Archive OSS applications; Sprint retrospective |

---

## Dev Environment Migration Schedule

**Sprint**: [Sprint Number]  
**Dates**: [Start Date] - [End Date]

### Batch 1 - Shadow Migration: [Date]

| Tenant | # Apps | Shadow Date | Verification Due | Planned Cutover | Status |
|--------|--------|-------------|------------------|-----------------|--------|
| tenant-alpha | 5 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-beta | 3 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-gamma | 8 | [Date] | [Date] | [Date] | 🔲 Not Started |

### Batch 2 - Shadow Migration: [Date]

| Tenant | # Apps | Shadow Date | Verification Due | Planned Cutover | Status |
|--------|--------|-------------|------------------|-----------------|--------|
| tenant-delta | 4 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-epsilon | 6 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-zeta | 2 | [Date] | [Date] | [Date] | 🔲 Not Started |

### Dev Environment Contacts

| Tenant | Primary Contact | Email | Backup Contact |
|--------|-----------------|-------|----------------|
| tenant-alpha | | | |
| tenant-beta | | | |
| tenant-gamma | | | |
| tenant-delta | | | |
| tenant-epsilon | | | |
| tenant-zeta | | | |

---

## NonProd Environment Migration Schedule

**Sprint**: [Sprint Number]  
**Dates**: [Start Date] - [End Date]

### Batch 1 - Shadow Migration: [Date]

| Tenant | # Apps | Shadow Date | Verification Due | Planned Cutover | Status |
|--------|--------|-------------|------------------|-----------------|--------|
| tenant-alpha | 5 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-beta | 3 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-gamma | 8 | [Date] | [Date] | [Date] | 🔲 Not Started |

### Batch 2 - Shadow Migration: [Date]

| Tenant | # Apps | Shadow Date | Verification Due | Planned Cutover | Status |
|--------|--------|-------------|------------------|-----------------|--------|
| tenant-delta | 4 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-epsilon | 6 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-zeta | 2 | [Date] | [Date] | [Date] | 🔲 Not Started |

### NonProd Environment Contacts

| Tenant | Primary Contact | Email | Backup Contact |
|--------|-----------------|-------|----------------|
| tenant-alpha | | | |
| tenant-beta | | | |
| tenant-gamma | | | |
| tenant-delta | | | |
| tenant-epsilon | | | |
| tenant-zeta | | | |

---

## Prod Environment Migration Schedule

**Sprint**: [Sprint Number]  
**Dates**: [Start Date] - [End Date]

### Batch 1 - Shadow Migration: [Date]

| Tenant | # Apps | Shadow Date | Verification Due | Planned Cutover | Status |
|--------|--------|-------------|------------------|-----------------|--------|
| tenant-alpha | 5 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-beta | 3 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-gamma | 8 | [Date] | [Date] | [Date] | 🔲 Not Started |

### Batch 2 - Shadow Migration: [Date]

| Tenant | # Apps | Shadow Date | Verification Due | Planned Cutover | Status |
|--------|--------|-------------|------------------|-----------------|--------|
| tenant-delta | 4 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-epsilon | 6 | [Date] | [Date] | [Date] | 🔲 Not Started |
| tenant-zeta | 2 | [Date] | [Date] | [Date] | 🔲 Not Started |

### Prod Environment Contacts

| Tenant | Primary Contact | Email | Backup Contact |
|--------|-----------------|-------|----------------|
| tenant-alpha | | | |
| tenant-beta | | | |
| tenant-gamma | | | |
| tenant-delta | | | |
| tenant-epsilon | | | |
| tenant-zeta | | | |

---

## Status Legend

| Status | Meaning |
|--------|---------|
| 🔲 Not Started | Migration not yet begun |
| 🔄 Shadow Active | Applications migrated to SaaS in shadow mode |
| 👀 Verification | Awaiting tenant verification |
| ✅ Verified | Tenant has signed off |
| 🔀 Cutover In Progress | Cutover being executed |
| ✅ Complete | Migration complete, stabilization period active |
| 📦 Archived | OSS applications archived |
| ⚠️ Blocked | Issue preventing progress |
| 🔙 Rolled Back | Cutover reverted to OSS |

---

## Key Dates Summary

| Milestone | Dev | NonProd | Prod |
|-----------|-----|---------|------|
| Sprint Start | [Date] | [Date] | [Date] |
| Tenant Notifications Sent | [Date] | [Date] | [Date] |
| Shadow Migrations Begin | [Date] | [Date] | [Date] |
| First Cutovers | [Date] | [Date] | [Date] |
| Environment Complete | [Date] | [Date] | [Date] |
| OSS Archive | [Date] | [Date] | [Date] |

---

## Scheduling Constraints

### Blackout Dates

The following dates are blocked for migrations:

| Date Range | Reason |
|------------|--------|
| [Date Range] | [Reason - e.g., Holiday freeze] |
| [Date Range] | [Reason - e.g., Major release] |

### Tenant-Specific Constraints

| Tenant | Constraint | Notes |
|--------|------------|-------|
| | | |

---

## Schedule Change Requests

To request a schedule change:

1. Contact your Tenant Liaison at least 48 hours before your scheduled date
2. Provide preferred alternative dates
3. Changes are subject to availability and batch constraints

---

## Communication Schedule

| When | What | Audience |
|------|------|----------|
| Sprint -1 Week | Migration overview and schedule preview | All tenants |
| Sprint Week 1 Day 3 | Confirmed schedule with specific dates | All tenants in environment |
| Shadow Day -1 | Reminder: Shadow migration tomorrow | Batch tenants |
| Shadow Day | Shadow migration complete notification | Migrated tenants |
| Verification Due -1 Day | Reminder: Verification due tomorrow | Unverified tenants |
| Cutover Day | Cutover scheduled notification | Batch tenants |
| Cutover Complete | Migration complete notification | Cut over tenants |

---

## Notes and Updates

*Use this section to document schedule changes, lessons learned, and important notes throughout the migration.*

| Date | Update |
|------|--------|
| | |