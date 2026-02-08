# Service Level: Design & Boundaries

Focus: The deployable unit zoom level - evaluating bounded context alignment, internal architecture, deployability, and error model design.

## Why This Matters

The service is the deployment boundary - the unit you build, test, and ship. A well-designed service has clear boundaries, clean internal architecture, and can evolve independently. A poorly designed service becomes a distributed monolith or an unmaintainable ball of mud.

## Review Checklist

### Bounded Context Design (DDD Strategic)

- [ ] **Context Boundary**: Is the service aligned to a single bounded context?
  - Does it serve one cohesive domain concept?
  - Or does it try to be multiple things (user management AND billing AND notifications)?
- [ ] **Ubiquitous Language**: Does the code vocabulary match the domain language?
  - Would a domain expert recognize the class and method names?
  - Are there translation mismatches between code and business terminology?
- [ ] **Model Integrity**: Is the domain model internally consistent?
  - Are there "foreign" concepts imported from other domains?
  - Does the model use names that mean different things in different parts of the code?
- [ ] **Translation at Boundaries**: Are external concepts translated at the edges?
  - Is there an Anti-Corruption Layer where upstream models are consumed?
  - Are external DTOs mapped to internal domain objects at the boundary?

### Architecture & Layering

- [ ] **Dependency Rule**: Do dependencies point inward?
  - Domain layer: No imports from infrastructure, UI, or external frameworks
  - Application layer: Orchestrates domain, depends on domain abstractions
  - Infrastructure layer: Implements interfaces defined in domain/application
- [ ] **Ports & Adapters**: Are external concerns behind interfaces?
  - Database access behind repository interfaces?
  - HTTP clients behind gateway interfaces?
  - Messaging behind publisher/subscriber interfaces?
- [ ] **Separation of Concerns**: Is business logic separate from infrastructure?
  - Can you swap the database without touching domain logic?
  - Can you change the HTTP framework without touching business rules?
- [ ] **Command/Query Separation**: Are reads and writes separated where appropriate?
  - Are query models optimized for read performance?
  - Are command models optimized for business rule enforcement?
  - Is CQRS applied where the read and write models genuinely differ?

### Deployability (Modern SE)

- [ ] **Independent Deployment**: Can this service be deployed without coordinating with others?
  - Are there implicit deployment dependencies?
  - Does it require other services to deploy simultaneously?
- [ ] **Configuration**: Are environment-specific values externalized?
  - No hardcoded URLs, connection strings, or secrets in code
  - Configuration loaded from environment variables or config service
  - Sensible defaults for development/local
- [ ] **Health Checks**: Does the service expose meaningful health endpoints?
  - Liveness: Is the process alive?
  - Readiness: Can it accept traffic? (dependencies available?)
  - Startup: Has initialization completed?
- [ ] **Graceful Startup/Shutdown**: Does the service handle lifecycle events cleanly?
  - Drains in-flight requests on shutdown
  - Completes pending work before exit
  - Deregisters from service discovery

### Error Model Design

- [ ] **Error Hierarchy**: Are errors well-categorized?
  - Transient vs permanent (retryable vs not)
  - Domain vs infrastructure (business rule violation vs connection failure)
  - Expected vs unexpected (validation failure vs null pointer)
- [ ] **Error Propagation**: Do errors cross boundaries appropriately?
  - Infrastructure errors translated to domain-level errors at boundary
  - No leaking of internal details (stack traces, SQL errors) to callers
  - Error codes/types are part of the public contract
- [ ] **Fail Fast**: Does the service validate early?
  - Input validation at the boundary, before processing begins
  - Precondition checks at the start of operations
  - Fast feedback on obviously invalid requests

## Anti-Patterns to Flag

### HIGH Severity

- **Shared database**: Two services reading/writing the same tables
  - Creates hidden coupling, prevents independent evolution
  - Fix: Define APIs between services, own your data
- **Distributed monolith**: Services that must deploy together
  - Shared libraries with domain logic
  - Synchronous call chains where all must be up
  - Fix: Reduce coupling, use async where appropriate
- **Domain logic in controllers**: Business rules in HTTP handlers/controllers
  - Makes logic untestable without HTTP
  - Fix: Move to domain/application layer

### MEDIUM Severity

- **Service too broad**: Multiple bounded contexts in one service
  - Signs: unrelated features, different change cadences, different stakeholders
  - Fix: Consider splitting along context boundaries
- **Chatty interface**: Too many fine-grained API calls needed
  - Signs: Client needs 5+ calls to complete one operation
  - Fix: Provide coarser-grained operations or aggregated endpoints
- **Missing ACL**: Directly using upstream models in domain code
  - Signs: External DTOs deep in business logic
  - Fix: Map to internal models at the boundary

### LOW Severity

- **Missing health checks**: No liveness/readiness probes
- **Hardcoded configuration**: URLs or settings in code
- **Inconsistent layering**: Some features bypass layers

## Layer Dependency Examples

```
# GOOD: Dependencies point inward

    ┌──────────────────────────────┐
    │      Infrastructure          │
    │  (DB adapters, HTTP, MQ)     │
    │                              │
    │  ┌────────────────────────┐  │
    │  │      Application       │  │
    │  │  (Use cases, handlers) │  │
    │  │                        │  │
    │  │  ┌──────────────────┐  │  │
    │  │  │     Domain       │  │  │
    │  │  │ (Entities, Rules)│  │  │
    │  │  └──────────────────┘  │  │
    │  └────────────────────────┘  │
    └──────────────────────────────┘

# Domain imports: nothing external
# Application imports: domain
# Infrastructure imports: domain + application
```

```python
# BAD: Domain depends on infrastructure
class OrderService:
    def create_order(self, data):
        db = SQLAlchemy.get_session()  # Infrastructure in domain
        order = Order(**data)
        db.add(order)
        requests.post('http://billing/charge', ...)  # HTTP in domain

# GOOD: Domain depends on abstractions
class OrderService:
    def __init__(self, repo: OrderRepository, billing: BillingGateway):
        self._repo = repo
        self._billing = billing

    def create_order(self, command: CreateOrder):
        order = Order.create(command)
        self._repo.save(order)
        self._billing.charge(order.total)
```

## Questions to Ask

1. Can this service be deployed independently of all other services?
2. If we swapped the database, how much code would change?
3. Does the service own its data, or does it share a database with others?
4. Would a domain expert recognize the bounded context this service represents?
5. Are external models translated at the boundary or used throughout?
