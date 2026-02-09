# Availability Pillar: Resilience & SLOs

Focus: Ensuring the system meets its Service Level Objectives and degrades gracefully under stress.

## Why This Matters

Availability isn't about never failing—it's about:
- Meeting commitments to users (SLOs)
- Failing gracefully when you must fail
- Limiting blast radius when things go wrong

A 99.9% SLO means you have 8.7 hours of downtime budget per year. Every code change either protects or threatens that budget.

## Review Checklist

### SLO Alignment

- [ ] Does this code path affect an SLO? Which one?
- [ ] What's the expected impact on error budget?
- [ ] Are there SLO-exempt paths? (health checks, admin endpoints)
- [ ] Is there SLO-based load shedding? (protect SLO by rejecting excess)

### Resilience Patterns

- [ ] **Circuit breakers**: Do calls to dependencies have circuit breakers?
- [ ] **Retries**: Are retries bounded with exponential backoff and jitter?
- [ ] **Timeouts**: Do all external calls have timeouts? Are they appropriate?
- [ ] **Bulkheads**: Are resources isolated? (separate thread pools, connection pools)
- [ ] **Fallbacks**: Is there degraded functionality when dependencies fail?

### Failure Handling

- [ ] What's the blast radius of this component failing?
- [ ] Are failures contained or do they cascade?
- [ ] Is there graceful degradation? (return cached data, reduced functionality)
- [ ] Are health checks meaningful? (not just "process is running")

### Load Management

- [ ] Is there backpressure? (bounded queues, rate limiting)
- [ ] Is there load shedding? (reject requests when overloaded)
- [ ] Are there admission controls? (don't start work you can't finish)
- [ ] Is work prioritized? (critical > background)

## SEEMS Deep Dive for Availability

| Category | Specific Questions |
|----------|-------------------|
| **Shared fate** | If this fails, what else fails? Is the blast radius acceptable? Are there shared connection pools, caches, or queues that create coupling? |
| **Excessive load** | What happens at 10x traffic? Is there fan-out that amplifies load? Are there retry storms waiting to happen? |
| **Excessive latency** | What's the worst-case latency? Are there unbounded operations (full table scans, unlimited pagination)? |
| **Single points of failure** | What's the redundancy story? Can this run in multiple regions/zones? What state needs to be replicated? |

## FaCTOR Deep Dive for Availability

| Property | Specific Questions |
|----------|-------------------|
| **Fault isolation** | Are there bulkheads between tenants? Between request types? Between dependencies? |
| **Availability** | What's the degraded mode? Is "something" better than "nothing"? |
| **Capacity** | Are limits defined? Connection pools, queue depths, in-flight requests? |
| **Redundancy** | What's the failover path? How long does failover take? Is there data loss during failover? |

## Anti-Patterns to Flag

- Unbounded retries (retry forever = amplify failures)
- Retries without backoff (retry storm generator)
- Retries without jitter (thundering herd)
- Missing timeouts on external calls
- Timeouts longer than user patience (30s timeout, 5s user wait)
- Health checks that don't check dependencies
- Health checks that are too sensitive (flapping)
- Synchronous calls to non-critical services
- No fallback when cache is unavailable
- Circuit breakers that never close (permanent degradation)
