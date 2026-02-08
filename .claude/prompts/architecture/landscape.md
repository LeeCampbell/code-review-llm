# Landscape Level: Ecosystem & Governance

Focus: The outermost zoom level - evaluating how systems integrate with each other, how architectural decisions are governed, and how the ecosystem evolves over time.

## Why This Matters

Individual services can be well-designed but the landscape can still be a mess. Without context maps, teams build redundant systems. Without integration standards, every connection is a bespoke snowflake. Without ADRs, decisions are made and forgotten. Without fitness functions, architecture erodes silently.

## Review Checklist

### DDD Context Maps

- [ ] **Context Map Exists**: Are relationships between bounded contexts documented?
  - Is there a visual map showing how contexts relate?
  - Is the map maintained as the system evolves?
- [ ] **Relationship Types**: Are upstream/downstream relationships explicit?
  - **Partnership**: Mutual cooperation, coordinated evolution
  - **Customer-Supplier**: Upstream serves downstream's needs
  - **Conformist**: Downstream conforms to upstream's model (no translation)
  - **Anti-Corruption Layer**: Downstream translates upstream's model
  - **Open Host Service**: Upstream provides a well-defined public API
  - **Published Language**: Shared interchange format (e.g., industry standard)
  - **Separate Ways**: No integration, each context is independent
- [ ] **Anti-Corruption Layers**: Are translation boundaries in place?
  - Where upstream models differ significantly from downstream needs?
  - At third-party integration points?
  - Between legacy and modern systems?

### Enterprise Integration Patterns (Hohpe & Woolf)

- [ ] **Integration Style**: Is the approach appropriate for the use case?
  - **File Transfer**: Batch, large volumes, loose coupling, high latency
  - **Shared Database**: Tight coupling, avoid across system boundaries
  - **Remote Procedure Call**: Synchronous, request/response, strong contracts
  - **Messaging**: Asynchronous, decoupled, resilient, eventually consistent
- [ ] **Message Design**: Are messages well-structured?
  - **Commands**: Imperative, directed at a specific consumer ("ProcessPayment")
  - **Events**: Past tense, broadcast to any interested party ("OrderPlaced")
  - **Documents**: Full state transfer for reference data ("ProductCatalog")
- [ ] **Routing Patterns**: Is message routing explicit and maintainable?
  - Content-Based Router: Routing by message content
  - Message Filter: Discarding irrelevant messages
  - Splitter/Aggregator: Breaking and reassembling messages
  - Is routing logic centralized or distributed appropriately?
- [ ] **Transformation**: Are data transformations transparent?
  - Are transformations documented and reversible?
  - Are there canonical data models for cross-system communication?
  - Are schema mappings versioned?
- [ ] **Error Handling**: Is there a dead-letter strategy?
  - What happens to messages that can't be processed?
  - Is there alerting on dead-letter queue growth?
  - Is there a process for replaying failed messages?
- [ ] **Idempotent Consumers**: Can consumers handle duplicates?
  - At-least-once delivery is the norm - are consumers prepared?
  - Are deduplication mechanisms in place?

### Architectural Governance

- [ ] **ADRs (Architecture Decision Records)**: Are decisions documented?
  - Context: What situation prompted the decision?
  - Decision: What was decided?
  - Consequences: What are the trade-offs?
  - Status: Proposed, accepted, deprecated, superseded
  - Are ADRs stored in version control alongside the code?
- [ ] **Fitness Functions**: Are architectural characteristics tested automatically?
  - **Dependency governance**: No circular deps, correct layer direction
  - **API compatibility**: Breaking change detection in CI
  - **Performance budgets**: Response time, throughput thresholds
  - **Size limits**: Package size, dependency count
  - Are fitness functions run in CI/CD?
- [ ] **Standards**: Are shared conventions documented and enforced?
  - API design guidelines (REST conventions, naming, versioning)
  - Error response format (consistent across services)
  - Logging format (structured, correlatable)
  - Authentication/authorization patterns
- [ ] **Versioning Strategy**: Is there a clear approach to API versioning?
  - How are breaking changes communicated?
  - What is the deprecation timeline?
  - How many versions are supported concurrently?

### Evolution & Change Management

- [ ] **Backward Compatibility**: Can systems evolve independently?
  - Can service A be updated without updating service B?
  - Are wire formats (JSON, Protobuf) extensible?
  - Is the Postel's Law applied? ("Be conservative in what you send, liberal in what you accept")
- [ ] **Deprecation Process**: Is there a clear path for retiring old interfaces?
  - Are deprecated endpoints marked with headers/annotations?
  - Is there a sunset date communicated to consumers?
  - Are usage metrics available to confirm no remaining consumers?
- [ ] **Migration Strategy**: Are there patterns for major changes?
  - **Strangler Fig**: New code gradually replaces old
  - **Parallel Run**: Old and new run simultaneously for comparison
  - **Branch by Abstraction**: Switch implementations behind an interface
- [ ] **Technology Radar**: Are technology choices deliberate?
  - Are new technology adoptions documented (ADR)?
  - Is there a process for evaluating new technologies?
  - Are there too many technologies solving the same problem?

## Anti-Patterns to Flag

### HIGH Severity

- **Distributed big ball of mud**: No clear boundaries, everything calls everything
  - Signs: Any change requires coordinating across many teams
  - Fix: Establish bounded contexts, define context map
- **Shared database across systems**: Multiple systems writing to the same tables
  - Signs: Schema changes break unknown consumers
  - Fix: APIs at system boundaries, data replication where needed
- **Undocumented integration points**: Services connected with no contract
  - Signs: "It just calls that endpoint" with no documentation
  - Fix: Formal contracts (OpenAPI, AsyncAPI), consumer-driven tests

### MEDIUM Severity

- **Missing ADRs**: Significant decisions with no documented rationale
  - Signs: "Why did we choose Kafka?" - nobody knows
  - Fix: Lightweight ADR process in version control
- **Spaghetti integration**: Point-to-point connections everywhere
  - Signs: n services with n*(n-1)/2 direct connections
  - Fix: Event bus, API gateway, or message broker for common patterns
- **Golden hammer**: Same technology for every problem
  - Signs: Using Kafka for request/response, REST for event streaming
  - Fix: Choose patterns that match the problem

### LOW Severity

- **No fitness functions**: Architecture drifts unchecked
  - Signs: Layer violations, unexpected dependencies appearing over time
  - Fix: Automated architecture tests in CI
- **Inconsistent API styles**: REST for some, gRPC for others, no pattern
  - Fix: Document standards, allow justified exceptions
- **Missing context map**: No visual representation of system relationships
  - Fix: Create and maintain a context map

## Integration Style Decision Guide

| Style | Coupling | Latency | Complexity | Best For |
| ----- | -------- | ------- | ---------- | -------- |
| **REST/gRPC** | Medium | Low | Low | Query, CRUD operations |
| **Messaging** | Low | Higher | Medium | Commands, events, decoupling |
| **Event Streaming** | Very Low | Variable | Higher | Real-time analytics, event sourcing |
| **File Transfer** | Very Low | Very High | Low | Batch processing, large datasets |
| **Shared Database** | Very High | Low | Low | **Avoid across system boundaries** |

## ADR Template

```markdown
# ADR-NNN: Title

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-XXX

## Context
What situation prompted this decision?

## Decision
What did we decide?

## Consequences
What are the trade-offs? What becomes easier? What becomes harder?
```

## Questions to Ask

1. If a new team needed to integrate with this system, could they do it from documentation alone?
2. Are there systems that call each other but have no formal contract?
3. What happens if we need to replace a core system? Is there a migration path?
4. Are architectural decisions documented, or do they only exist in people's heads?
5. Is the architecture actively governed (fitness functions) or passively eroding?
