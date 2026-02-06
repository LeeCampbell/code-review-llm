# Governance, Privacy & Lifecycle Pillar

Focus: Compliance, data ethics, and full lifecycle management of data assets.

## Why This Matters

Data governance failures lead to regulatory fines (GDPR, CCPA), reputational damage, and legal liability. Without clear ownership, data becomes an orphan that nobody maintains. Without lifecycle management, storage costs grow unbounded and compliance becomes impossible.

## Review Checklist

### Privacy & Compliance

- [ ] **Data Classification**: Is the data explicitly classified?
  - PII (Personally Identifiable Information)
  - Confidential (business-sensitive)
  - Internal (general business use)
  - Public (safe to share externally)
- [ ] **Masking & Obfuscation**: Are sensitive columns protected according to classification?
  - Emails: masked or hashed
  - Phone numbers: last 4 digits only
  - Health information: tokenized
  - Financial data: encrypted
- [ ] **Purpose Limitation**: Is data collection and processing limited to a specific, valid business purpose?
  - Is the purpose documented?
  - Would collection pass the "newspaper test"?

### Lifecycle Management

- [ ] **Retention & Purging**: Is there defined logic for data lifecycle?
  - How long is data kept? (regulatory minimum, business need)
  - Is there automated archiving to cold storage?
  - Is there automated purging when retention expires?
- [ ] **Backup Strategy**: Is there a defined backup approach?
  - Backup frequency (daily, hourly, continuous)
  - Backup retention period
  - Point-in-time recovery capability
- [ ] **Disaster Recovery**: Is there a documented recovery process?
  - RPO (Recovery Point Objective): How much data loss is acceptable?
  - RTO (Recovery Time Objective): How long can we be down?
  - Has recovery been tested?
- [ ] **Right to be Forgotten**: Does the design support GDPR deletion requests?
  - Can specific user data be identified and removed?
  - Crypto-shredding for encrypted data?
  - Downstream propagation of deletions?

### Lineage & Ownership

- [ ] **Provenance**: Is the lineage of data clear?
  - Can we trace back to the authoritative source system?
  - Are all transformations documented?
  - Is lineage captured automatically (not just documented)?
- [ ] **Ownership Assignment**: Are owners clearly defined?
  - **Business Owner**: Accountable for data value and business rules
  - **Technical Owner**: Accountable for quality and operations
  - Are owners documented in metadata/catalog?

## Common Anti-Patterns

### HIGH Severity

```sql
-- PII in logs or debug tables
INSERT INTO debug_log (timestamp, context)
VALUES (NOW(), 'Processing user: email=john@example.com, ssn=123-45-6789');
-- PII exposed in operational logs
```

```sql
-- No retention policy
CREATE TABLE user_events (
    event_id BIGINT,
    user_id INT,
    event_data JSON,
    created_at TIMESTAMP
    -- No partition for lifecycle management
    -- No TTL or retention policy defined
);
-- Table grows forever
```

```python
# Unmasked PII in analytics
df_analytics = df[['user_id', 'email', 'phone', 'purchase_amount']]
df_analytics.to_parquet('s3://analytics-bucket/user_purchases/')
# Raw PII in analytics layer
```

### MEDIUM Severity

```sql
-- No ownership metadata
CREATE TABLE customer_metrics (
    -- No comments documenting owner
    -- No catalog registration
    -- No contact information for questions
);
```

```sql
-- No lineage tracking
CREATE TABLE derived_metrics AS
SELECT customer_id, SUM(amount) as total
FROM source_table  -- Which source_table? From which system?
GROUP BY customer_id;
-- Transformation not documented
```

## Data Classification Guide

| Classification | Examples | Required Controls |
| -------------- | -------- | ----------------- |
| **PII** | Name, email, SSN, phone | Encryption, masking, access logging, retention limits |
| **Confidential** | Revenue, strategy, trade secrets | Encryption, need-to-know access |
| **Internal** | Operational metrics, general business | Standard access controls |
| **Public** | Marketing content, public filings | No restrictions |

## PII Masking Techniques

| Technique | Use Case | Example |
| --------- | -------- | ------- |
| **Hashing** | Pseudonymization for analytics | `SHA256(email)` → `a7f3d...` |
| **Tokenization** | Reversible masking | `email` → `TOKEN_12345` (vault lookup) |
| **Redaction** | Partial visibility | `john@example.com` → `j***@e***.com` |
| **Generalization** | Reduce precision | `age: 34` → `age_band: 30-40` |
| **Encryption** | Access-controlled visibility | AES-256 encrypted, key-managed |

## Retention Policy Template

```yaml
data_product: customer_transactions
classification: PII
retention:
  active_storage: 2_years
  archive_storage: 7_years
  purge_after: 7_years
backup:
  frequency: daily
  retention: 30_days
  rpo: 24_hours
  rto: 4_hours
gdpr:
  deletion_supported: true
  deletion_method: crypto_shredding
ownership:
  business_owner: customer_analytics_team
  technical_owner: data_platform_team
  contact: data-support@company.com
```

## Questions to Ask

1. What happens if a user requests their data be deleted?
2. How long are we required to keep this data? How long do we actually keep it?
3. If this data was leaked, what would be the impact?
4. Who do I contact if I have questions about this data?
5. Can we trace this data back to its original source?
6. Has disaster recovery been tested for this data?
