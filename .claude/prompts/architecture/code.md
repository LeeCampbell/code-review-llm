# Code Level: Structure & Quality

Focus: The innermost zoom level - evaluating classes, functions, and modules for structural correctness, adherence to design principles, and testability.

## Why This Matters

Code-level quality is the foundation of all higher-level architecture. Poorly structured code propagates upward - a tangled module becomes a tangled service becomes a tangled system. Good architecture starts with clean code.

## Review Checklist

### SOLID Principles

- [ ] **Single Responsibility (SRP)**: Does each class/module have one reason to change?
  - Can you describe the class's purpose in one sentence without "and"?
  - If the class changes, is it always for the same business reason?
- [ ] **Open/Closed (OCP)**: Can behavior be extended without modifying existing code?
  - Are extension points provided (interfaces, strategy pattern, plugins)?
  - Does adding a new variant require modifying existing switch/if chains?
- [ ] **Liskov Substitution (LSP)**: Can subtypes replace their base types without breaking behavior?
  - Do subclasses honor the contracts of their parents?
  - Are there subclasses that throw "not implemented" exceptions?
- [ ] **Interface Segregation (ISP)**: Are interfaces focused and cohesive?
  - Do clients use all methods of the interfaces they depend on?
  - Are there "fat" interfaces that force implementors to provide stubs?
- [ ] **Dependency Inversion (DIP)**: Do high-level modules depend on abstractions?
  - Does business logic import infrastructure (database, HTTP, filesystem)?
  - Are dependencies injected rather than constructed internally?

### DDD Tactical Patterns

- [ ] **Entities**: Do entities have clear identity?
  - Is identity established at creation and immutable?
  - Are equality checks based on identity, not attributes?
- [ ] **Value Objects**: Are immutable concepts modeled as value objects?
  - Are concepts like Money, Email, DateRange modeled as types (not primitives)?
  - Are value objects immutable with equality based on attributes?
- [ ] **Aggregates**: Are transactional boundaries well-defined?
  - Are aggregates small (prefer smaller aggregates)?
  - Is there a clear aggregate root that controls access?
  - Are cross-aggregate references by ID only (not direct object references)?
- [ ] **Repositories**: Is persistence abstracted?
  - Do repositories return domain objects (not DTOs or database rows)?
  - Is the repository interface defined in the domain layer?
- [ ] **Domain Events**: Are significant state changes captured as events?
  - Do events represent facts about what happened (past tense)?
  - Are events immutable once created?

### Code Quality (Modern SE)

- [ ] **Testability**: Can this code be unit tested in isolation?
  - Are dependencies injectable?
  - Are side effects isolated behind interfaces?
  - Can the code be tested without a database, network, or filesystem?
- [ ] **Complexity**: Is cyclomatic complexity reasonable?
  - Are methods short and focused (prefer < 20 lines)?
  - Are deeply nested conditionals flattened (guard clauses, early returns)?
  - Are complex boolean expressions extracted to named methods?
- [ ] **Cohesion**: Do classes/modules group related behavior?
  - Do all methods in a class operate on the same data?
  - Would splitting the class result in two equally useful classes?
- [ ] **Coupling**: Is coupling between modules loose?
  - Are dependencies explicit (no hidden globals, singletons, or service locators)?
  - Is the dependency graph a tree (not a web)?
  - Are circular dependencies absent?
- [ ] **Naming**: Do names reflect the domain (ubiquitous language)?
  - Would a domain expert recognize the names?
  - Are technical implementation names kept out of the domain layer?
- [ ] **DRY/YAGNI**: Is there the right level of abstraction?
  - Is logic duplicated across multiple locations?
  - Are there abstractions that only have one implementation (premature)?
  - Is there unused code or dead code paths?

## Anti-Patterns to Flag

### HIGH Severity

- **God class**: Module with too many responsibilities (> 500 lines, > 10 dependencies)
- **Circular dependencies**: Module A depends on B which depends on A
- **Leaky abstraction**: Domain objects expose persistence details (e.g., `@Entity` annotations on domain classes)
- **Missing boundaries**: Business logic mixed with infrastructure in the same class

### MEDIUM Severity

- **Primitive obsession**: Using strings for emails, ints for IDs instead of typed value objects
- **Anemic domain model**: Classes with only getters/setters and no behavior
- **Feature envy**: Methods that use another class's data more than their own
- **Deep inheritance**: More than 2-3 levels of inheritance (prefer composition)
- **Shotgun surgery**: A single change requires modifying many classes

### LOW Severity

- **Magic numbers**: Unexplained literal values without named constants
- **Inconsistent naming**: Mixed conventions within the same module
- **Long parameter lists**: Methods taking > 3-4 parameters (consider parameter objects)

## Code Smell Examples

```python
# BAD: God class with mixed responsibilities
class OrderService:
    def create_order(self, items): ...
    def calculate_tax(self, amount): ...
    def send_email(self, recipient): ...
    def generate_pdf(self, order): ...
    def validate_credit_card(self, card): ...

# GOOD: Single responsibility
class OrderService:
    def __init__(self, tax_calc, notifier):
        self._tax = tax_calc
        self._notifier = notifier

    def create_order(self, items): ...
```

```python
# BAD: Primitive obsession
def create_user(email: str, age: int, currency: str, amount: float): ...

# GOOD: Value objects
def create_user(email: Email, age: Age, price: Money): ...
```

```python
# BAD: Domain depends on infrastructure
from sqlalchemy import Column, Integer, String

class Order:  # Domain entity importing ORM
    id = Column(Integer, primary_key=True)
    status = Column(String)

# GOOD: Clean domain, persistence in adapter
class Order:  # Pure domain
    def __init__(self, id: OrderId, status: OrderStatus): ...
```

## Questions to Ask

1. If a new developer joined, could they understand this module in under 30 minutes?
2. Can you test this code without standing up infrastructure?
3. Does changing one requirement affect only one module?
4. Would a domain expert recognize the vocabulary used in the code?
5. Are the module's dependencies obvious from its constructor/imports?
