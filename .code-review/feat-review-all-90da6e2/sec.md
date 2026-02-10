# Security Review -- Maturity Assessment

## Maturity Status

| Level | Status | Summary |
|-------|--------|---------|
| Hygiene | ⚠️ | Embedded production database references and PII-bearing SQL in committed source; HTTP-only internal API communication without TLS |
| Level 1 -- Foundations | ❌ | No authentication, authorization, input validation, secrets management, or session handling present |
| Level 2 -- Operational Maturity | 🔒 | Locked -- Level 1 not passed |
| Level 3 -- Excellence | 🔒 | Locked -- Level 2 not passed |

**Immediate Action:** Remove hardcoded production database schema names (CHU_PROD, LLS_PROD, POK_PROD, CAM_PROD) and PII-bearing SQL queries from committed source code in `python/code_review.py` and `results/` directories. These reveal internal infrastructure topology and handle user identifiers (USER_ID, PLAYER_ID, ACCOUNT_ID, address data) in plaintext strings committed to version control.

---

## Hygiene

### Hygiene Gate Failures

| Test | Finding | Location |
|------|---------|----------|
| **Irreversible** | Production database schema names and table structures for 4 production environments (CHU_PROD, LLS_PROD, POK_PROD, CAM_PROD) are hardcoded in committed source. Once pushed to any remote, this internal infrastructure topology is permanently exposed. | `python/code_review.py:131-498`, `results/001-sql code-r1-1.5b/input.txt`, `results/002-sql-code-r1-14b/input.txt` |
| **Regulated** | SQL queries reference PII columns (USER_ID, PLAYER_ID, ACCOUNT_ID, ADDRESS_SUBDIVISION_CODE, GEO_LOCATION_SUBDIVISION_CODE) and financial data (WIN_AMOUNT, PLAY_AMOUNT, CURRENCY_WON, CURRENCY_WAGERED). The embedded SQL also references `V_ACCOUNT_CONTACT_ADDRESS` tables containing address data. If this repository is or becomes public, it constitutes disclosure of PII processing patterns and internal data schemas, potentially relevant under GDPR/CCPA. | `python/code_review.py:131-498` |

---

## Level 1 -- Foundations -- Detailed Assessment

- ❌ **Authentication and authorization are applied consistently on all protected paths** -- Missing: The Python script (`python/code_review.py`) makes an HTTP POST to the Ollama API at `http://ollama-service:11434/api/chat` (line 7, 32) with zero authentication. No API keys, tokens, or any auth mechanism is present. The Ollama service in `docker-compose.yml` is exposed on port 11434 with no access control.

- ❌ **External input is validated before processing** -- Missing: The response from the Ollama API (`response.json()` at line 35) is consumed without any validation. Dictionary keys are accessed directly (lines 37-48) with no error handling, type checking, or schema validation. A malformed response would cause an unhandled exception that could leak stack trace information.

- ❌ **Secrets are loaded from environment or external store, not source** -- Missing: While no traditional secrets (API keys, passwords) are present, the hardcoded Ollama service URL (`http://ollama-service:11434/api/chat`) should be configurable via environment variables. More critically, the production database schema references embedded in string literals are a form of internal infrastructure secrets committed to source.

- ❌ **Sessions have explicit expiry and rotation** -- Not applicable in the current architecture (no sessions exist), but the absence of any session or connection management for the HTTP client is notable -- `requests.post()` is called with no timeout parameter, meaning a hung Ollama service would block indefinitely.

---

## Higher Levels -- Preview

> **Level 2 -- Hardening**: Security-relevant actions produce audit records; Exposed endpoints enforce rate limits; Roles default to least privilege; Error responses do not leak internal state or stack traces.

> **Level 3 -- Excellence**: Security checks run automatically in the build pipeline; Encryption parameters are configurable; Dependencies are scanned for known vulnerabilities automatically.

---

## Detailed Findings

| Priority | Severity | Maturity | Confidence | STRIDE | Location | Finding | Recommendation |
|----------|----------|----------|------------|--------|----------|---------|----------------|
| 1 | MEDIUM | HYG | HIGH | I (Information Disclosure) | `python/code_review.py:131-498` | Production database schema names, table names, column names, and join relationships for 4 production environments (CHU_PROD, LLS_PROD, POK_PROD, CAM_PROD) are embedded as string literals in committed source code. This reveals internal infrastructure topology including database naming conventions, schema structure, and data relationships. | Extract SQL to external files excluded via `.gitignore`, or parameterize database references. Remove production identifiers from version control history using `git filter-branch` or BFG Repo Cleaner if this repo has been shared. |
| 2 | MEDIUM | HYG | HIGH | I (Information Disclosure) | `python/code_review.py:131-498`, `results/001-sql code-r1-1.5b/input.txt`, `results/002-sql-code-r1-14b/input.txt` | SQL queries reference PII-adjacent columns (USER_ID, PLAYER_ID, ACCOUNT_ID) and sensitive location data (ADDRESS_SUBDIVISION_CODE, GEO_LOCATION_SUBDIVISION_CODE) as well as financial amounts (WIN_AMOUNT, PLAY_AMOUNT). The `results/` directory also contains the full SQL with production references as stored output. This reveals data handling patterns that could aid reconnaissance. | Remove `results/` directory from version control or redact production identifiers. Add `results/` to `.gitignore`. |
| 3 | LOW | L1 | HIGH | D (Denial of Service) | `python/code_review.py:32` | `requests.post(url, json=payload)` is called with no `timeout` parameter. If the Ollama service becomes unresponsive, the Python process will block indefinitely. This is a trivial DoS vector if the service is exposed. | Add a timeout parameter: `requests.post(url, json=payload, timeout=300)` |
| 4 | LOW | L1 | HIGH | T (Tampering) | `python/code_review.py:35-48` | The response from the Ollama API is parsed and fields are accessed without validation (`data['model']`, `data['message']`, etc.). A tampered or malformed response could cause KeyError exceptions. No response schema validation exists. | Add try/except around response parsing, validate expected keys exist, and validate response status code before parsing JSON. |
| 5 | LOW | L1 | MEDIUM | I (Information Disclosure) | `python/code_review.py:7` | The Ollama API endpoint uses plaintext HTTP (`http://ollama-service:11434/api/chat`). While this is within a Docker network, any network-level attacker who gains access to the Docker bridge network can intercept all LLM prompts and responses, which include production SQL queries with PII column references. | Configure TLS for inter-service communication, or ensure the Docker network is isolated and document the accepted risk. |
| 6 | LOW | L1 | MEDIUM | I (Information Disclosure) | `python/code_review.py:33,50-54` | Ollama API responses including full model output are printed to stdout (lines 33, 50-54). In a production or shared environment, stdout may be captured in logs. The model responses could contain sensitive analysis of the production SQL queries. | Implement structured logging with appropriate log levels rather than bare `print()` statements. |
| 7 | LOW | L1 | MEDIUM | E (Elevation of Privilege) | `.devcontainer/docker-compose.yml:24-29` | The Ollama service container is granted access to ALL GPU devices (`count: all`) with full nvidia capabilities. This is an overly broad privilege grant. If the container is compromised, the attacker has full access to all GPU resources on the host. | Scope GPU access to only the required number of devices (e.g., `count: 1`). |
| 8 | LOW | L1 | MEDIUM | S (Spoofing) | `.devcontainer/docker-compose.yml:18-19` | The Ollama service exposes port 11434 to the host (`ports: - 11434:11434`) with no authentication. Any process on the host or any host-network-accessible attacker can send requests to the Ollama API, potentially using it to run arbitrary LLM inference. | Bind the port to localhost only (`127.0.0.1:11434:11434`) or remove the port mapping if only inter-container communication is needed. |
| 9 | LOW | L1 | MEDIUM | D (Denial of Service) | `.devcontainer/deepseek-r1.001.5b.dockerfile:6`, `.devcontainer/deepseek-r1.014b.dockerfile:4` | Dockerfiles pull LLM models during build (`ollama pull deepseek-r1:14b`) using a pattern of `ollama serve & sleep 5 && ollama pull`. The 5-second sleep is a race condition -- if Ollama takes longer to start, the pull will fail, causing a silent build failure. This is a reliability/availability issue. | Use a proper health check or retry loop to wait for Ollama to be ready before pulling the model. |

---

## What's Good

- **No hardcoded secrets (API keys, passwords, tokens)**: The codebase does not contain any traditional secrets. No API keys, passwords, or authentication tokens are committed to source.

- **Dependencies are minimal and well-known**: The `requirements.txt` contains only three standard packages (`boto3`, `python-dotenv`, `requests`), reducing the attack surface from third-party code.

- **`python-dotenv` is included**: The presence of `python-dotenv` in requirements suggests the intent to use environment variables for configuration, even though this is not yet implemented in the main script.

- **`.gitignore` exists**: While minimal (only `.DS_Store`), a `.gitignore` file is in place and can be extended.

- **Docker network isolation**: Services communicate over a dedicated Docker network (`llm-network`), providing a degree of network-level isolation between the application and the LLM service.

- **No use of dangerous Python functions**: The codebase does not use `eval()`, `exec()`, `pickle`, `subprocess`, `os.system()`, or `shell=True`. The `from ast import literal_eval` import on line 4 of `code_review.py` is imported but never used, and `literal_eval` is the safe alternative to `eval()` in any case.

- **Claude settings use explicit permission allow-lists**: The `.claude/settings.json` file uses a deny-by-default approach with explicit allow-lists for permitted bash commands, which is a good security practice for agent tooling.
