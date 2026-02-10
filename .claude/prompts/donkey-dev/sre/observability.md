# Observability Pillar: Visibility & Understanding

Focus: Giving visibility into code behavior, highlighting bottlenecks, errors, and enabling teams to build SLIs for their SLOs.

## Why This Matters

You can't fix what you can't see. Observability is about:
- Understanding system behavior in production
- Detecting problems before users report them
- Answering novel questions about system state

## The Three Pillars

### Logging

- [ ] Are key operations logged? (requests, state changes, decisions)
- [ ] Is log level appropriate? (ERROR for errors, INFO for operations, DEBUG for details)
- [ ] Is structured logging used? (JSON/key-value, not string interpolation)
- [ ] Are correlation IDs propagated across service boundaries?
- [ ] Is PII/sensitive data excluded or masked?
- [ ] Are log volumes reasonable? (no spam in hot paths)

### Metrics

- [ ] Are SLI-relevant metrics exposed? (latency, error rate, throughput)
- [ ] Are metrics labeled appropriately? (endpoint, status, customer tier)
- [ ] Are histograms used for latencies? (not averages)
- [ ] Are counters used for rates? (not gauges)
- [ ] Is cardinality bounded? (no unbounded label values)
- [ ] Are business metrics captured? (not just technical)

### Tracing

- [ ] Are spans created for significant operations?
- [ ] Is trace context propagated across async boundaries?
- [ ] Are span attributes meaningful? (not just operation name)
- [ ] Are errors recorded on spans?
- [ ] Is sampling appropriate for the traffic volume?

## Review Checklist

### SLI Derivability

- [ ] Can request latency be measured from this code?
- [ ] Can error rates be calculated by error type?
- [ ] Can throughput be measured?
- [ ] Can saturation be determined? (queue depth, connection pool usage)

### Debugging Support

- [ ] Can you trace a request through the system?
- [ ] Can you identify slow operations?
- [ ] Can you see retry attempts and their outcomes?
- [ ] Can you correlate logs, metrics, and traces?

### Signal Presence

- [ ] Do critical failure paths emit a metric or log that could be alerted on?
- [ ] Can you distinguish between symptoms and causes from emitted signals?
- [ ] Are there leading indicators emitted? (queue depth, connection pool usage, error rate changes)

## SEEMS Focus for Observability

| Category | Observability-Specific Concern |
|----------|-------------------------------|
| **Excessive load** | Are load metrics visible? Can you see request rates, queue depths? |
| **Excessive latency** | Are latency percentiles captured? Can you identify slow dependencies? |
| **Misconfiguration** | Are config values logged/exposed as metrics? |

## FaCTOR Focus for Observability

| Property | Observability-Specific Concern |
|----------|-------------------------------|
| **Capacity** | Can you see resource utilization? Connection pools, memory, CPU? |
| **Timeliness** | Can you measure latency against SLO targets? |

## Anti-Patterns to Flag

- `console.log` / `print` statements instead of structured logging
- Logging entire objects (PII risk, log bloat)
- Metrics with unbounded cardinality (user_id as label)
- Missing units on metrics (is this milliseconds or seconds?)
- Tracing only happy paths (errors not captured)
- No way to correlate a user complaint to system behavior
- Averages instead of percentiles for latency
