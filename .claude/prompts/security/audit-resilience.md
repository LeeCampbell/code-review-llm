# Audit & Resilience Pillar

Focus: Ensuring accountability through audit trails and protecting service availability from abuse.

## STRIDE Coverage

This pillar covers:

- **Repudiation** - Can users deny their actions? Is there an audit trail?
- **Denial of Service** - Can attackers disrupt service availability?

## Why This Matters

Without audit trails, you can't investigate incidents, prove compliance, or hold bad actors accountable. Without DoS protection, a single attacker can take down your service, affecting all users.

## Review Checklist

### Audit Logging

- [ ] Are security-relevant events logged? (auth, access, changes)
- [ ] Do logs include who, what, when, where, outcome?
- [ ] Are logs tamper-evident? (append-only, signed, or external)
- [ ] Is PII handled appropriately in logs? (masked or excluded)
- [ ] Are logs retained for compliance requirements?
- [ ] Can logs be correlated across services? (request IDs)

### What to Log

| Event Type | Required Fields |
| ---------- | --------------- |
| Authentication | User ID, timestamp, success/failure, IP, user agent |
| Authorization failures | User ID, resource, action attempted, reason denied |
| Data access | User ID, resource type, resource ID, action |
| Data modification | User ID, resource, old value (masked), new value (masked) |
| Admin actions | Admin ID, action, target, parameters |
| Security events | Event type, severity, details, source IP |

### Log Integrity

- [ ] Are logs written to append-only storage?
- [ ] Are log timestamps from trusted sources?
- [ ] Is log forwarding secure? (TLS, authentication)
- [ ] Are logs backed up and retained?
- [ ] Can log tampering be detected?

### Rate Limiting

- [ ] Are public endpoints rate-limited?
- [ ] Are rate limits per-user and per-IP?
- [ ] Are expensive operations (search, export) limited?
- [ ] Is there graduated response? (slow down before block)
- [ ] Are rate limit headers returned? (X-RateLimit-*)

### Resource Bounds

- [ ] Are request sizes limited?
- [ ] Are upload sizes limited?
- [ ] Are query result sizes bounded?
- [ ] Are timeouts set for external calls?
- [ ] Are connection pools bounded?
- [ ] Are recursive/nested operations depth-limited?

### Abuse Prevention

- [ ] Is CAPTCHA used for sensitive operations?
- [ ] Are automated attacks detectable? (anomaly detection)
- [ ] Is there IP blocking capability?
- [ ] Are abuse patterns monitored?
- [ ] Is there graceful degradation under load?

## Common Vulnerability Patterns

### HIGH Confidence Findings

```python
# Missing audit log for sensitive operation
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    # No audit trail - who deleted? when? why?

# Unbounded query (DoS)
@app.route('/search')
def search():
    results = db.query(Item).filter(Item.name.like(f"%{term}%")).all()
    return results  # Could return millions of rows

# No rate limiting on auth endpoint
@app.route('/login', methods=['POST'])
def login():
    # Allows unlimited password attempts
    if check_password(request.form['password']):
        return create_session()
```

### MEDIUM Confidence Findings

```python
# Audit log missing critical context
logger.info(f"User action performed")  # Missing who, what, outcome

# Regex DoS (ReDoS)
pattern = re.compile(r'^(a+)+$')
pattern.match(user_input)  # Exponential time on malicious input

# Algorithmic complexity attack
def process_json(data):
    # Deeply nested JSON can cause stack overflow
    return json.loads(data)  # No depth limit
```

## DoS Attack Vectors to Consider

| Vector | Example | Mitigation |
| ------ | ------- | ---------- |
| **Request flooding** | Millions of requests/sec | Rate limiting, CDN |
| **Large payloads** | 1GB POST body | Request size limits |
| **Slow attacks** | Slowloris, slow POST | Connection timeouts |
| **Algorithmic** | ReDoS, hash collision | Input validation, limits |
| **Resource exhaustion** | Connection pool drain | Pool limits, timeouts |
| **Application logic** | Expensive searches | Query limits, caching |

## Audit Log Format Example

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "user.data.access",
  "severity": "info",
  "actor": {
    "user_id": "user-123",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  },
  "action": "read",
  "resource": {
    "type": "document",
    "id": "doc-456"
  },
  "outcome": "success",
  "request_id": "req-789"
}
```

## Anti-Patterns to Flag

- Security events with no logging
- Logs that can be modified by users
- Missing rate limits on authentication
- Unbounded queries without pagination
- No request size limits
- Missing timeouts on external calls
- Regex with user input (ReDoS risk)
- Recursive processing without depth limits
- No CAPTCHA on public forms
- Logs containing plaintext secrets/passwords
