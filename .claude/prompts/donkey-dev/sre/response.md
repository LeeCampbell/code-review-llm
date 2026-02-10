# Response Pillar: Incident Handling & Recovery

Focus: The effective response to failure events through incident processes, runbooks, and disaster recovery.

## Why This Matters

Services fail. Often at 3am. When they do, operators need:
- Clear signals about what's wrong
- Enough context to diagnose quickly
- Safe remediation paths

Code that fails silently or cryptically extends incidents and burns out on-call engineers.

## Review Checklist

### Error Messages & Context

- [ ] Are error messages actionable? Do they explain what went wrong AND what to do?
- [ ] Is sufficient context captured? (request IDs, user IDs, relevant state)
- [ ] Are errors distinguishable? Can you tell a config error from a dependency failure from a bug?
- [ ] Are sensitive details redacted from error output?

### Failure Modes

- [ ] Are failure modes explicit? (not buried in generic catch blocks)
- [ ] Is there appropriate error categorization? (retryable vs permanent, client vs server)
- [ ] Are partial failures handled? (some items succeed, some fail)
- [ ] Is there dead letter handling for unprocessable items?

### Recovery Paths

- [ ] Can the system recover without human intervention where possible?
- [ ] Are there circuit breakers to prevent cascade during recovery?
- [ ] Is state recoverable after restart? (checkpoints, idempotent replay)
- [ ] Are there safe manual intervention points? (pause, drain, force-retry)

### Runbook Readiness

- [ ] Would an on-call engineer understand this failure from logs alone?
- [ ] Are there links to documentation or runbooks in error output?
- [ ] Is there clear ownership? (which team, which service)
- [ ] Are escalation paths clear?

## SEEMS Focus for Response

| Category | Response-Specific Concern |
|----------|--------------------------|
| **Misconfiguration** | Can config errors be diagnosed from error messages? Are config values logged at startup? |
| **Excessive latency** | Are timeouts reported with context about what was being waited on? |
| **Shared fate** | When a dependency fails, is it clear which dependency and why? |

## FaCTOR Focus for Response

| Property | Response-Specific Concern |
|----------|--------------------------|
| **Fault isolation** | Are failures attributed to the correct component? |
| **Output correctness** | Are error responses well-formed? Do they follow API contracts? |

## Anti-Patterns to Flag

- Generic error messages: "An error occurred" / "Something went wrong"
- Swallowed exceptions with no logging
- Stack traces exposed to end users
- Missing correlation IDs across service boundaries
- Errors that require code reading to understand
- No distinction between "should retry" and "don't bother"
