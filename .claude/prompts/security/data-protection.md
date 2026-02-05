# Data Protection Pillar

Focus: Protecting data confidentiality and integrity - ensuring sensitive information isn't exposed and data cannot be tampered with.

## STRIDE Coverage

This pillar covers:

- **Information Disclosure** - Can attackers access data they shouldn't see?
- **Tampering** - Can attackers modify data without detection?

## Why This Matters

Data breaches are among the most costly security incidents. Exposed PII triggers regulatory penalties (GDPR, CCPA), reputational damage, and legal liability. Data tampering can lead to fraud, corruption, and system compromise.

## Review Checklist

### Sensitive Data Handling

- [ ] Is PII identified and classified? (names, emails, SSN, financial data)
- [ ] Is sensitive data encrypted at rest?
- [ ] Is sensitive data encrypted in transit? (TLS 1.2+)
- [ ] Is sensitive data masked in logs?
- [ ] Is there data minimization? (only collect what's needed)
- [ ] Is there data retention policy? (delete when no longer needed)

### Cryptography

- [ ] Are modern algorithms used? (AES-256, RSA-2048+, SHA-256+)
- [ ] Are deprecated algorithms avoided? (MD5, SHA1, DES, RC4)
- [ ] Is key management secure? (not hardcoded, rotated)
- [ ] Are IVs/nonces unique and random?
- [ ] Is authenticated encryption used where needed? (AES-GCM)
- [ ] Are cryptographic libraries well-maintained?

### Secrets Management

- [ ] Are secrets stored in environment variables or secret managers?
- [ ] Are secrets NOT in source code, configs, or logs?
- [ ] Are API keys scoped and rotatable?
- [ ] Is there separation between dev/staging/prod secrets?
- [ ] Are secrets masked in error messages and stack traces?

### Data Integrity

- [ ] Are checksums/signatures used for critical data?
- [ ] Is input validated before processing?
- [ ] Are database constraints enforced?
- [ ] Is there integrity verification for file uploads?
- [ ] Are tamper-evident logs maintained?

### Output Encoding

- [ ] Is output encoded for the target context? (HTML, JSON, SQL, shell)
- [ ] Are Content-Type headers set correctly?
- [ ] Is user content sanitized before rendering?
- [ ] Are security headers present? (CSP, X-Content-Type-Options)

## Common Vulnerability Patterns

### HIGH Confidence Findings

```python
# Sensitive data in logs
logger.info(f"User login: {username}, password: {password}")

# Hardcoded secrets
API_KEY = "sk-1234567890abcdef"
encryption_key = b"mysecretkey12345"

# Weak encryption
from Crypto.Cipher import DES  # DES is broken
cipher = DES.new(key, DES.MODE_ECB)  # ECB mode is insecure

# SQL query result exposed
@app.route('/debug')
def debug():
    return str(db.execute("SELECT * FROM users"))  # Full table dump
```

### MEDIUM Confidence Findings

```python
# PII in URL (logged by default)
redirect(f"/profile?ssn={user.ssn}")

# Missing TLS verification
requests.get(url, verify=False)

# Sensitive data in error response
except Exception as e:
    return {"error": str(e), "query": sql_query}  # Leaks internals
```

## Data Classification Guide

| Classification | Examples | Required Protection |
| -------------- | -------- | ------------------- |
| **Critical** | Passwords, payment cards, health records | Encryption at rest + transit, access logging, minimal retention |
| **Sensitive** | PII, emails, addresses | Encryption in transit, access control, masking in logs |
| **Internal** | Business data, analytics | Access control, audit trail |
| **Public** | Marketing content | Integrity protection only |

## Anti-Patterns to Flag

- Logging sensitive data (passwords, tokens, PII)
- Secrets in source code or config files
- Using broken cryptographic algorithms
- Exposing internal errors to users
- Missing encryption for sensitive data at rest
- Transmitting sensitive data over HTTP
- Storing passwords in plaintext or reversible encryption
- Excessive data in API responses (over-fetching)
- Debug endpoints in production
- Backup files accessible via web (.bak, .sql, .dump)
