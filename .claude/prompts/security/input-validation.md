# Input Validation Pillar

Focus: Preventing injection attacks and ensuring all external input is properly validated before use.

## STRIDE Coverage

This pillar covers:

- **Tampering** - Specifically injection attacks where malicious input alters intended behavior

## Why This Matters

Injection attacks remain the most dangerous vulnerability class. SQL injection, command injection, and XSS can lead to complete system compromise, data theft, and malware distribution. Most are trivially exploitable once found.

## Review Checklist

### SQL Injection

- [ ] Are parameterized queries/prepared statements used?
- [ ] Is ORM used with parameter binding?
- [ ] Is dynamic SQL avoided? If not, is it properly escaped?
- [ ] Are stored procedures using parameterized inputs?
- [ ] Is database user privilege minimized?

### Command Injection

- [ ] Is shell execution avoided where possible?
- [ ] Are arguments passed as arrays (not concatenated strings)?
- [ ] Is user input ever passed to shell commands?
- [ ] Are allowlists used for permitted commands?
- [ ] Is subprocess used instead of os.system/shell=True?

### Cross-Site Scripting (XSS)

- [ ] Is output encoded for HTML context?
- [ ] Are dangerous APIs avoided? (innerHTML, dangerouslySetInnerHTML, v-html)
- [ ] Is Content-Security-Policy header set?
- [ ] Are user uploads validated and served safely?
- [ ] Is context-aware encoding used? (HTML vs JS vs URL vs CSS)

### Path Traversal

- [ ] Is user input used in file paths?
- [ ] Are paths canonicalized and validated?
- [ ] Is there a allowlist of permitted directories?
- [ ] Are symbolic links handled safely?

### Deserialization

- [ ] Is untrusted data deserialized?
- [ ] Are safe deserialization methods used?
- [ ] Is pickle/marshal avoided for untrusted data?
- [ ] Are type constraints enforced?

### Template Injection

- [ ] Is user input ever part of template strings?
- [ ] Are sandbox/autoescape enabled?
- [ ] Is template logic separated from user data?

## Common Vulnerability Patterns

### HIGH Confidence Findings

```python
# SQL Injection
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# Command Injection
os.system(f"convert {user_filename} output.png")
subprocess.call(f"grep {search_term} logs.txt", shell=True)

# XSS - React
<div dangerouslySetInnerHTML={{__html: userContent}} />

# XSS - Template
return render_template_string(f"<h1>{user_input}</h1>")

# Path Traversal
file_path = f"/uploads/{user_provided_filename}"
return send_file(file_path)

# Unsafe Deserialization
data = pickle.loads(request.data)  # RCE if attacker controls input
```

### MEDIUM Confidence Findings

```python
# Second-order SQL injection (data from DB used unsafely)
username = get_from_database(user_id)  # Could contain SQL
query = f"SELECT * FROM logs WHERE user = '{username}'"

# DOM XSS (JavaScript)
element.innerHTML = location.hash.substring(1);

# YAML deserialization with unsafe loader
data = yaml.load(user_input)  # Use yaml.safe_load instead
```

## Framework-Specific Considerations

| Framework | XSS Protection | Notes |
| --------- | -------------- | ----- |
| React | Auto-escapes by default | Dangerous: `dangerouslySetInnerHTML` |
| Angular | Auto-escapes by default | Dangerous: `bypassSecurityTrustHtml` |
| Vue | Auto-escapes by default | Dangerous: `v-html` directive |
| Django | Auto-escapes by default | Dangerous: `|safe` filter, `mark_safe()` |
| Rails | Auto-escapes by default | Dangerous: `raw()`, `html_safe` |
| Express/EJS | Manual escaping needed | Use `<%= %>` not `<%- %>` |

## Input Validation Principles

1. **Validate on the server** - Never trust client-side validation alone
2. **Allowlist over blocklist** - Define what IS allowed, not what isn't
3. **Validate type, length, format, range** - Be strict
4. **Encode output** - Context-appropriate encoding on output
5. **Use frameworks** - Don't roll your own sanitization

## Anti-Patterns to Flag

- String concatenation for SQL queries
- User input in shell commands
- `eval()`, `exec()` with user input
- Direct HTML rendering of user content
- File operations with user-controlled paths
- Regex with user input (ReDoS potential)
- XML parsing with external entities enabled (XXE)
- Deserializing untrusted data
- Using blocklists instead of allowlists
- Client-side only validation
