# Data Modeling & Architecture Pillar

Focus: Structural correctness, interoperability, and long-term maintainability of data assets.

## Why This Matters

Poor data architecture creates technical debt that compounds over time. Schema decisions made today affect every downstream consumer. Breaking changes cascade through the data mesh, and poorly designed models become maintenance nightmares.

## Review Checklist

### Domain & Schema Design

- [ ] **Domain Boundaries**: Does the data model adhere to its bounded context without creating tight coupling or circular dependencies with other domains?
- [ ] **Polysemes & Identifiers**: Are shared concepts ('User', 'Product', 'Order') correctly mapped using global identifiers to ensure interoperability across the mesh?
- [ ] **Schema Normalization**: Is the schema design appropriate for the use case?
  - Operational/transactional: 3NF for consistency
  - Analytical: Star/Snowflake for query performance
  - Streaming: Event-sourced for temporal queries

### Interoperability & Standards

- [ ] **Naming Conventions**: Do table, column, and entity names follow organization standards?
  - Consistent casing (snake_case preferred)
  - No ambiguous acronyms
  - Business-meaningful names
- [ ] **Standardized Ports**: Are input/output interfaces defined using agreed standards?
  - SQL for structured queries
  - Iceberg/Delta for table formats
  - JSON/Avro/Protobuf for serialization
- [ ] **Metadata Alignment**: Do attribute names and definitions align with the Enterprise Data Model or Business Glossary to prevent semantic drift?

### Maintainability & Evolution

- [ ] **Schema Stability**: Does the change introduce breaking schema changes?
  - Column renames or removals
  - Type changes (narrowing)
  - Semantic changes to existing fields
- [ ] **Versioning Strategy**: Is there a versioning approach (SemVer) to protect downstream consumers?
- [ ] **Simplicity**: Is the model arranged for readability?
  - Entities grouped logically
  - Avoiding unnecessary complexity
  - Clear relationships

### Data Contracts

- [ ] **Contract Definition**: Is there a formal contract specifying:
  - Schema (fields, types, constraints)
  - Quality expectations (freshness, completeness)
  - SLAs (availability, latency)
- [ ] **Breaking Change Process**: Is there a process for communicating and managing breaking changes to consumers?

## Common Anti-Patterns

### HIGH Severity

```sql
-- Tight coupling: query reaches across schema boundaries into other domains
SELECT o.*, c.*, p.*, i.*
FROM sales.orders o
JOIN customer_service.customers c ON o.customer_id = c.id  -- Customer domain
JOIN marketing.products p ON o.product_id = p.id           -- Product domain
JOIN warehouse.inventory i ON p.id = i.product_id          -- Inventory domain
-- If any domain changes its internal schema, this query breaks.
-- Consume from published data contracts instead of internal tables.
```

```sql
-- Deadly diamond: same order data arrives via two paths with different timing
--
--   raw.orders ──→ enrichment.order_details ──→ analytics.daily_revenue
--       │                                            ↑
--       └────→ fraud.scored_orders ──────────────────┘
--
-- Path A (enrichment) completes in minutes. Path B (fraud scoring) takes hours.
-- If daily_revenue reads from both, it sees today's enriched orders but
-- yesterday's fraud scores — totals are wrong, fraud flags are stale.
INSERT INTO analytics.daily_revenue
SELECT d.order_id, d.amount, f.fraud_score
FROM enrichment.order_details d
JOIN fraud.scored_orders f ON d.order_id = f.order_id
WHERE d.order_date = CURRENT_DATE;
-- Fix: declare both paths as upstream dependencies so the target only
-- runs when both have completed for the same partition.
```

```sql
-- Breaking change: column rename without versioning
ALTER TABLE users RENAME COLUMN user_name TO username;
-- All downstream consumers break immediately
```

### MEDIUM Severity

```sql
-- Inconsistent naming
SELECT
    user_id,           -- snake_case
    firstName,         -- camelCase
    LAST_NAME,         -- UPPER_SNAKE
    EmailAddress       -- PascalCase
FROM users;
```

```sql
-- Missing global identifier for polyseme
CREATE TABLE orders (
    customer_id INT,   -- Local ID only
    -- Should include: customer_global_id UUID for cross-domain joins
);
```

## Schema Design Decision Guide

| Use Case | Recommended Schema | Rationale |
| -------- | ------------------ | --------- |
| OLTP / Transactions | 3NF | Update anomaly prevention, consistency |
| OLAP / Analytics | Star/Snowflake | Query performance, aggregation |
| Event Streaming | Event-sourced | Temporal queries, replay capability |
| ML Features | Wide tables | Feature access patterns |
| Data Lake raw | Schema-on-read | Flexibility, late binding |

## Questions to Ask

1. Who are the consumers of this data? What are their access patterns?
2. How will this schema evolve over the next 2 years?
3. What happens if we need to rename or remove a field?
4. Can this be understood by someone new to the domain?
5. Does this create dependencies on other domain's internal schemas?
