# Delivery Pillar: Deployment Safety & Velocity

Focus: Ensuring code can be deployed repeatedly, rapidly, and safely.

## Why This Matters

The best code is worthless if you can't ship it safely. Delivery is about:
- Deploying with confidence
- Rolling back without data loss
- Separating deployment from release

## Review Checklist

### Deployment Safety

- [ ] Can this be deployed incrementally? (canary, blue-green, rolling)
- [ ] What happens if deployment fails mid-way? (partial rollout)
- [ ] Are there database migrations? Are they backward compatible?
- [ ] Is the change backward compatible with running instances?
- [ ] Can old and new versions coexist during deployment?

### Rollback Readiness

- [ ] Can this be rolled back? What's the rollback procedure?
- [ ] Is there data that can't be "un-migrated"?
- [ ] Are there external dependencies on the new behavior?
- [ ] How long until rollback is no longer possible?

### Feature Management

- [ ] Should this be behind a feature flag?
- [ ] Can this be dark-launched? (deployed but not activated)
- [ ] Is there a kill switch for this functionality?
- [ ] Can it be enabled per-tenant/percentage/region?

### Configuration Management

- [ ] Are new configs backward compatible?
- [ ] What are the safe defaults?
- [ ] Can config be changed without redeployment?
- [ ] Is there config validation before applying?

### Database Changes

- [ ] Are schema changes backward compatible?
- [ ] Is the migration reversible?
- [ ] What's the migration duration at production scale?
- [ ] Are there lock concerns? (table locks during migration)
- [ ] Is there a data backfill? How long will it take?

## SEEMS Focus for Delivery

| Category | Delivery-Specific Concern |
|----------|--------------------------|
| **Misconfiguration** | Can a config change cause outage? Are there safe defaults? Is there config validation? |
| **Shared fate** | Does this deployment affect other services? Are there coordinated deployments required? |

## FaCTOR Focus for Delivery

| Property | Delivery-Specific Concern |
|----------|--------------------------|
| **Output correctness** | Will old and new versions produce consistent results during rollout? |
| **Availability** | Can you deploy without downtime? What's the availability impact of rollback? |

## Deployment Patterns to Look For

### Safe Patterns

- Feature flags with gradual rollout
- Database migrations that add before remove
- API versioning with deprecation periods
- Canary deployments with automatic rollback
- Blue-green with instant switchover capability

### Risky Patterns (Flag These)

- Schema changes that break old code
- Removing API fields without deprecation
- Migrations that lock tables at scale
- Deploy-time data transformations
- Coordinated multi-service deployments
- "Flag day" changes (all-or-nothing)

## Anti-Patterns to Flag

- Non-reversible database migrations
- Breaking API changes without versioning
- Config changes that require coordinated deployment
- Removing feature flags before stabilization
- Deployments that require downtime
- Missing health checks for new functionality
- Hardcoded values that should be configurable
- Secrets in code or config files
- Dependencies on deployment order
