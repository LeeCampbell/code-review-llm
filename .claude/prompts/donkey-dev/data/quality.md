# Data Quality, Trust & Timeliness Pillar

Focus: The "Trusted and Timely" mantra - ensuring data products meet consumer expectations for accuracy, freshness, and usability.

## Why This Matters

Data is only valuable if it can be trusted. Late data leads to stale decisions. Undocumented data becomes "tribal knowledge" that leaves when people do. Quality issues erode confidence and lead to shadow data systems.

## Review Checklist

### Timeliness & Freshness

- [ ] **Freshness SLOs**: Are there defined Service Level Objectives for data timeliness?
  - "Data available within 15 minutes of event"
  - "Daily snapshot by 6am UTC"
  - Does the design support meeting these SLOs?
- [ ] **Processing Latency**: Is the gap between Event Time and Processing Time measured?
  - Is this latency acceptable for the use case?
  - Are there alerts if latency exceeds threshold?
- [ ] **Update Frequency**: Is the schedule aligned with business need?
  - Batch vs streaming appropriateness
  - Over-engineering (real-time when daily is fine)
  - Under-engineering (daily when hourly is needed)

### Accuracy & Integrity

- [ ] **Automated Constraints**: Are there automated checks for:
  - **Validity**: Value ranges, formats, referential integrity
  - **Uniqueness**: No duplicate records on primary keys
  - **Completeness**: Required fields are not NULL, expected row counts
- [ ] **Bitemporality**: Does the model support both:
  - Transaction time (when recorded in system)
  - Valid time (when true in reality)
  - Critical for handling late-arriving data and corrections
- [ ] **Reconciliation**: Is there a mechanism to verify data matches source?
  - Row count comparisons
  - Sum/checksum verification
  - Sample record validation

### Usability & Documentation

- [ ] **Consumer Documentation**: Is the data product documented so consumers can use it without "tribal knowledge"?
  - Field descriptions and business definitions
  - Example queries
  - Known limitations and caveats
  - Computational notebooks for exploration
- [ ] **Discoverability**: Is the data registered in the catalog?
  - Clear metadata (description, owner, freshness)
  - Tags for searchability
  - Sample data preview

### Observability & Anomaly Detection

- [ ] **Volume Monitoring**: Are expected row counts defined and monitored?
  - Alert if load delivers 0 rows
  - Alert if volume is 10x or 0.1x expected
  - Historical volume trending
- [ ] **Distribution Checks**: Are value distributions monitored?
  - Mean/median shift detection
  - NULL percentage changes
  - Cardinality changes (new values appearing)
- [ ] **Schema Change Detection**: Will you be alerted if upstream schema changes?
  - New columns added
  - Columns removed or renamed
  - Type changes

## Common Anti-Patterns

### HIGH Severity

```sql
-- No uniqueness constraint on business key
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50),  -- No UNIQUE constraint!
    amount DECIMAL
);
-- Duplicates will silently accumulate
```

```python
# Silent data loss on type mismatch
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
# Invalid values become NaN with no logging
```

### MEDIUM Severity

```sql
-- No freshness tracking
CREATE TABLE daily_metrics (
    metric_date DATE,
    value DECIMAL
    -- Missing: loaded_at TIMESTAMP, source_freshness TIMESTAMP
);
-- Can't tell if data is stale
```

```python
# Undocumented magic numbers
df = df[df['status'].isin([1, 3, 7])]
# What do these status codes mean? Where is this documented?
```

## Data Quality Dimensions

| Dimension | Definition | How to Check |
| --------- | ---------- | ------------ |
| **Accuracy** | Data matches real-world truth | Reconciliation with source |
| **Completeness** | All required data present | NULL checks, row counts |
| **Consistency** | Same data across systems | Cross-system comparisons |
| **Timeliness** | Data available when needed | Freshness SLO monitoring |
| **Validity** | Data conforms to rules | Constraint checks, format validation |
| **Uniqueness** | No duplicates | Primary key enforcement |

## Great Expectations Patterns

Common expectations to implement:

```python
# Completeness
expect_column_values_to_not_be_null(column="customer_id")
expect_table_row_count_to_be_between(min_value=1000, max_value=100000)

# Validity
expect_column_values_to_be_between(column="amount", min_value=0)
expect_column_values_to_match_regex(column="email", regex=r"^[\w.-]+@[\w.-]+\.\w+$")

# Uniqueness
expect_column_values_to_be_unique(column="order_id")
expect_compound_columns_to_be_unique(column_list=["customer_id", "order_date"])

# Freshness (custom)
expect_column_max_to_be_between(column="event_timestamp",
    min_value=datetime.now() - timedelta(hours=1),
    max_value=datetime.now())
```

## Questions to Ask

1. If this data is wrong, how would we know?
2. What's the SLO for freshness? Is it documented?
3. Can a new team member understand this data without asking someone?
4. What happens if source data arrives late?
5. Are there automated checks, or do we rely on consumers to report issues?
