# System Level: Service Interactions & Stability

Focus: The inter-service zoom level - evaluating how services communicate, protect themselves from failure, and maintain contracts with each other.

## Why This Matters

Most production incidents originate at integration points between services. As Michael Nygard writes in Release It!: "Integration points are the number-one killer of systems." A well-designed system has explicit contracts, stability patterns at every boundary, and services that can fail independently.

## Review Checklist

### Stability Patterns (Release It!)

- [ ] **Circuit Breaker**: Are calls to downstream services protected?
  - Is there a circuit breaker on every external call?
  - Are failure thresholds appropriate (not too sensitive, not too lenient)?
  - Is there a half-open state to test recovery?
  - Are circuit breaker states observable (metrics, logs)?
- [ ] **Bulkhead**: Are failure domains isolated?
  - Are thread pools / connection pools separated per dependency?
  - Can one failing dependency exhaust resources for all?
  - Are critical and non-critical paths isolated?
- [ ] **Timeout**: Do all inter-service calls have explicit timeouts?
  - Are timeouts set on every outbound call (HTTP, gRPC, database)?
  - Are timeout values appropriate (not too long, not too short)?
  - Do timeouts cascade correctly (inner < outer)?
- [ ] **Shed Load**: Can the system reject work when overwhelmed?
  - Are there admission controls (rate limiting, queue depth limits)?
  - Does the system return appropriate responses when shedding (429, 503)?
  - Is load shedding observable?
- [ ] **Backpressure**: Can consumers signal producers to slow down?
  - In async systems: Are queues bounded? What happens when full?
  - In sync systems: Do clients respect rate limit headers?
  - Is there graduated response (slow down before reject)?
- [ ] **Fail Fast**: Do services fail fast when dependencies are unavailable?
  - Do health checks verify dependency availability?
  - Do services refuse traffic if not ready (readiness probe)?
  - Are known-bad requests rejected immediately (validation)?
- [ ] **Governor**: Are there limits on resource consumption?
  - Connection pool sizes defined and bounded?
  - Thread pool sizes defined and bounded?
  - Queue depths limited?
  - Memory limits set?

### API Contracts & Communication

- [ ] **Contract Design**: Are API contracts explicit and versioned?
  - Is there a formal contract (OpenAPI, Protobuf, GraphQL schema)?
  - Are contracts stored in version control?
  - Are contracts tested (consumer-driven contract tests)?
- [ ] **Backward Compatibility**: Do changes maintain compatibility?
  - Are new fields additive (not replacing)?
  - Are removed fields deprecated first?
  - Is there a versioning strategy (URL, header, content negotiation)?
- [ ] **Idempotency**: Are operations idempotent where needed?
  - Can retries cause duplicate side effects?
  - Are idempotency keys supported for mutations?
  - Are GET requests truly safe and idempotent?
- [ ] **Communication Style**: Is sync vs async chosen appropriately?
  - Synchronous: For queries, immediate responses needed
  - Asynchronous: For commands, fire-and-forget, long-running operations
  - Events: For notifications, multiple consumers, eventual consistency

### Coupling & Cohesion (System Level)

- [ ] **Service Coupling**: Are services loosely coupled?
  - Can services evolve independently?
  - Are there runtime dependencies that prevent independent deployment?
  - Does service A need to know about service B's internal structure?
- [ ] **Temporal Coupling**: Are there implicit ordering dependencies?
  - Must service A call B before C?
  - Are there timing assumptions between services?
  - Can operations be reordered without breaking behavior?
- [ ] **Data Coupling**: Do services share databases or data stores?
  - Are there shared tables, schemas, or databases?
  - Does one service read another service's data directly?
  - Fix: Expose data through APIs, replicate if needed
- [ ] **Choreography vs Orchestration**: Is the coordination style appropriate?
  - Choreography (events): Services react to events independently
  - Orchestration (commands): A central coordinator directs the flow
  - Is the chosen style appropriate for the complexity of the flow?

## Stability Anti-Patterns (Release It!)

### HIGH Severity

- **Unprotected integration point**: External call with no timeout, no circuit breaker
  ```python
  # BAD: No timeout, no circuit breaker
  response = requests.get(f"http://downstream/api/data")

  # GOOD: Protected with timeout and circuit breaker
  @circuit_breaker(failure_threshold=5, recovery_timeout=30)
  def get_data():
      return requests.get(
          f"http://downstream/api/data",
          timeout=(3, 10)  # connect, read
      )
  ```
- **Cascading failure**: One service's failure bringing down others
  - Signs: All services fail when one dependency is slow
  - Fix: Bulkheads, circuit breakers, async communication
- **Unbounded result sets**: No pagination or limits on cross-service queries
  ```python
  # BAD: Could return millions of rows
  orders = order_service.get_all_orders()

  # GOOD: Bounded and paginated
  orders = order_service.get_orders(page=1, limit=100)
  ```

### MEDIUM Severity

- **Blocked threads**: Synchronous calls to slow dependencies blocking thread pools
  - Signs: Thread pool exhaustion under load
  - Fix: Async calls, timeout + circuit breaker, bulkhead thread pools
- **Self-denial attack**: System features that create load spikes
  - Signs: Marketing email blast causes cache stampede
  - Fix: Stagger processing, pre-warm caches
- **Dogpile**: Thundering herd on cache expiry or restart
  - Signs: All instances expire cache simultaneously, all hit database
  - Fix: Jittered expiry, cache warming, request coalescing

### LOW Severity

- **Missing contract tests**: No automated verification of API compatibility
- **Inconsistent error responses**: Different error formats across services
- **Missing correlation IDs**: No request tracing across service boundaries

## Communication Pattern Decision Guide

| Pattern | Use When | Example |
| ------- | -------- | ------- |
| **Request/Response (sync)** | Need immediate answer, low latency required | Get user profile, validate payment |
| **Request/Async Response** | Request needed but response can wait | Place order, process claim |
| **Event Notification** | Multiple consumers, producer doesn't care who listens | Order placed, user registered |
| **Event-Carried State Transfer** | Consumers need data, avoid runtime coupling | Product catalog updated (with full product data) |
| **Command** | Directing a specific service to do something | Process payment, send notification |

## Questions to Ask

1. What happens if this downstream service is unavailable for 5 minutes?
2. What happens if this downstream service is slow (10x normal latency)?
3. Can one service's failure bring down the entire system?
4. Are all external calls protected with timeouts and circuit breakers?
5. If we deploy service A, do we also need to deploy service B?
