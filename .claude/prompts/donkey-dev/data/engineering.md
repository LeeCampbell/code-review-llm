# Engineering Logic & Code Quality Pillar

Focus: Validating the correctness of code (SQL/Python/Spark) before it touches data, ensuring robust engineering practices.

## Why This Matters

Data pipelines run in production, often unattended. Bugs don't just crash - they silently corrupt data, creating issues that propagate downstream and may not be discovered until business decisions have been made on bad data.

## Review Checklist

### Logic Verification (Unit Testing)

- [ ] **Transformation Logic**: Are complex transformations backed by automated unit tests?
  - Currency conversions
  - Date calculations
  - Aggregations with edge cases
  - Business rule implementations
- [ ] **Query Correctness**: Has SQL logic been tested for edge cases?
  - NULL handling in JOINs (LEFT vs INNER behavior)
  - Fan-out risks (1-to-many joins inflating counts)
  - Off-by-one errors in date ranges (< vs <=)
  - Empty result set handling
- [ ] **Deterministic Output**: Is the transformation idempotent?
  - Same input → same output
  - No dependency on processing order
  - No use of non-deterministic functions (RANDOM, NOW) without seeding

### Code Efficiency & Performance

- [ ] **Query Cost**: Have expensive operations been optimized?
  - Full table scans when partition pruning is possible
  - Missing indexes on join columns
  - Cartesian joins (missing join conditions)
  - SELECT * when only specific columns needed
- [ ] **Incremental Processing**: Does code support CDC efficiently?
  - Watermark-based incremental loads
  - Partition-aware processing
  - Avoiding full reprocessing of historical data
- [ ] **Deadly Diamonds**: Does logic avoid split-brain scenarios?
  - Data arriving via multiple paths with different timing
  - Race conditions in parallel processing
  - Inconsistent state from partial updates

### Development Standards

- [ ] **Declarative Definitions**: Are pipelines defined declaratively?
  - Data Product Manifests
  - dbt models with documented dependencies
  - Infrastructure as Code for resources
- [ ] **Modularity**: Is code modular and reusable?
  - Common transformations extracted to shared functions
  - No copy-paste logic across pipelines
  - Clear separation of concerns

### Error Handling & Recovery

- [ ] **Validation Failure**: What happens when incoming data fails validation?
  - Dead-letter queue for bad records?
  - Rejection logging with context?
  - Alerting on validation failures?
- [ ] **Partial Failure**: Can processing resume without duplicates or gaps?
  - Checkpoint/savepoint mechanism?
  - Idempotent writes (MERGE/UPSERT)?
  - Transaction boundaries?
- [ ] **Circuit Breakers**: Are there thresholds that halt processing?
  - Error rate exceeds X%
  - Volume anomaly (10x expected)
  - Source system health check

## Common Anti-Patterns

### HIGH Severity

```sql
-- Fan-out without aggregation (inflates metrics)
SELECT
    orders.order_id,
    SUM(orders.amount) as total  -- WRONG: inflated by line_items join
FROM orders
JOIN line_items ON orders.order_id = line_items.order_id
GROUP BY orders.order_id;
-- Should aggregate line_items first, then join
```

```python
# Non-deterministic transformation
df['processed_at'] = datetime.now()  # Different on each run
df['random_sample'] = random.random()  # Non-reproducible
```

```sql
-- Silent NULL handling issue
SELECT customer_id, SUM(amount)
FROM orders
WHERE status = 'completed'
  AND region = @region  -- If @region is NULL, no rows match
GROUP BY customer_id;
```

### MEDIUM Severity

```sql
-- Full table scan when partition available
SELECT * FROM events
WHERE event_date = '2024-01-15';
-- Should use: WHERE event_date = '2024-01-15' AND partition_date = '2024-01-15'
```

```python
# No error handling for external call
result = requests.get(api_url).json()  # What if API fails?
df['enriched'] = result['data']
```

```sql
-- Implicit type coercion
SELECT * FROM users WHERE user_id = '123';
-- user_id is INT, comparing to STRING - may prevent index use
```

## Idempotency Patterns

| Pattern | Implementation | Use Case |
| ------- | -------------- | -------- |
| **MERGE/UPSERT** | `MERGE INTO target USING source ON key WHEN MATCHED UPDATE WHEN NOT MATCHED INSERT` | Dimension updates |
| **Delete-Insert** | `DELETE WHERE partition = X; INSERT ...` | Partition replacement |
| **Versioned Insert** | `INSERT ... ON CONFLICT DO NOTHING` with version column | Event deduplication |
| **Tombstone** | Soft delete with `deleted_at` timestamp | Audit trail required |

## Testing Strategy

| Test Type | What to Test | Tools |
| --------- | ------------ | ----- |
| **Unit** | Individual transformation functions | pytest, dbt tests |
| **Contract** | Schema, nullability, ranges | Great Expectations |
| **Integration** | End-to-end pipeline flow | dbt build, Airflow tests |
| **Performance** | Query execution time, cost | EXPLAIN ANALYZE, query profiles |
