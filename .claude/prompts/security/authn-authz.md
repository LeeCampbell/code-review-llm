# Authentication & Authorization Pillar

Focus: Identity verification and access control - ensuring users are who they claim to be and can only access what they're permitted to.

## STRIDE Coverage

This pillar covers:

- **Spoofing** - Can attackers impersonate legitimate users?
- **Elevation of Privilege** - Can attackers gain unauthorized access levels?

## Why This Matters

Authentication and authorization flaws are consistently in the OWASP Top 10. A single bypass can compromise the entire system, giving attackers access to all user data or administrative functions.

## Review Checklist

### Authentication Mechanisms

- [ ] Are credentials transmitted securely? (HTTPS, no query params)
- [ ] Is password hashing using modern algorithms? (bcrypt, argon2, scrypt - NOT MD5/SHA1)
- [ ] Are failed login attempts rate-limited?
- [ ] Is there account lockout after repeated failures?
- [ ] Are password reset tokens single-use and time-limited?
- [ ] Is multi-factor authentication available for sensitive operations?

### Session Management

- [ ] Are session tokens cryptographically random and sufficiently long?
- [ ] Are sessions invalidated on logout?
- [ ] Is session fixation prevented? (new session ID after login)
- [ ] Are session cookies marked HttpOnly, Secure, SameSite?
- [ ] Is there session timeout for inactive sessions?
- [ ] Are concurrent sessions handled appropriately?

### JWT/Token Security

- [ ] Is the algorithm explicitly specified? (no "alg: none" attacks)
- [ ] Are tokens validated on every request?
- [ ] Is the secret key sufficiently strong and properly stored?
- [ ] Are tokens short-lived with refresh mechanism?
- [ ] Is token revocation possible?
- [ ] Are claims validated (issuer, audience, expiration)?

### Authorization Logic

- [ ] Is authorization checked on every protected endpoint?
- [ ] Is there separation between authentication and authorization?
- [ ] Are default permissions restrictive? (deny by default)
- [ ] Is RBAC/ABAC implemented correctly?
- [ ] Are horizontal access controls in place? (user A can't access user B's data)
- [ ] Are vertical access controls in place? (regular user can't access admin)

### Privilege Escalation Prevention

- [ ] Are admin functions protected by additional verification?
- [ ] Is privilege inheritance handled correctly?
- [ ] Are role changes audited?
- [ ] Is there separation of duties for critical operations?
- [ ] Are API keys scoped to minimum necessary permissions?

## Common Vulnerability Patterns

### HIGH Confidence Findings

```
# Missing auth check on sensitive endpoint
@app.route('/admin/users')
def list_users():
    return User.query.all()  # No @login_required, no role check

# Broken object-level authorization (IDOR)
@app.route('/api/documents/<doc_id>')
def get_document(doc_id):
    return Document.query.get(doc_id)  # No check if user owns document

# Hardcoded credentials
DB_PASSWORD = "admin123"  # Hardcoded secret

# Weak JWT validation
token = jwt.decode(token, options={"verify_signature": False})
```

### MEDIUM Confidence Findings

```
# Timing attack on authentication
if user.password == provided_password:  # Not constant-time comparison

# Session not regenerated after login
session['user_id'] = user.id  # Same session ID before/after auth

# Overly permissive CORS
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

## Anti-Patterns to Flag

- Authentication bypass via parameter manipulation (`?admin=true`)
- Missing authorization on state-changing operations
- Client-side only access control
- Predictable session/token values
- Credentials in URL parameters or logs
- Default/weak credentials in code
- Missing re-authentication for sensitive operations
- Trust based on client-provided role claims
