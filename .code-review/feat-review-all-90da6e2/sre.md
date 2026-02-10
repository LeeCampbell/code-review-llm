# SRE Review -- Maturity Assessment

## Maturity Status

| Level | Status | Summary |
|-------|--------|---------|
| Hygiene | ⚠️ | HTTP call to Ollama has no timeout; could block indefinitely and exhaust resources under failure |
| Level 1 -- Foundations | ❌ | No health checks, no error handling, no structured logging, no timeouts on external calls |
| Level 2 -- Operational Maturity | 🔒 | Blocked: L1 not passed. No SLOs, no failure isolation, no degradation paths |
| Level 3 -- Excellence | 🔒 | Blocked: L2 not passed. No CI/CD pipeline, no capacity enforcement, no failure tests |

**Immediate Action:** Add a timeout to the `requests.post()` call in `python/code_review.py:32`. Without a timeout, a hung Ollama service will block the caller indefinitely, potentially exhausting threads/connections in any system that invokes this code. This is a Hygiene-level finding (Total -- can render the caller completely unresponsive).

---

## Hygiene

| Severity | Maturity | Category | Location | Finding | Recommendation |
|----------|----------|----------|----------|---------|----------------|
| HIGH | HYG | Excessive Latency / Timeliness | `python/code_review.py:32` | `requests.post(url, json=payload)` has no `timeout` parameter. If the Ollama service hangs or is unreachable, the caller blocks indefinitely. This can exhaust all available threads/workers. (Total: can take down the entire calling process.) | Add `timeout=(connect_seconds, read_seconds)` e.g. `requests.post(url, json=payload, timeout=(5, 300))`. The read timeout should be generous since LLM inference is slow, but must be finite. |
| HIGH | HYG | Misconfiguration | `.devcontainer/entrypoint.*.sh:9` | All entrypoint scripts use `sleep 5` as a readiness gate for Ollama. If Ollama takes longer than 5 seconds to start (common under load or with large models), the subsequent `ollama run` may fail silently or behave unpredictably. (Total: service starts in a broken state, all requests fail.) | Replace the hardcoded `sleep 5` with a readiness loop that polls the Ollama health endpoint (e.g. `until curl -sf http://localhost:11434/; do sleep 1; done`). |

---

## Level 1 -- Foundations -- Detailed Assessment

- ❌ **Health checks reflect real readiness** -- No health check endpoint exists. The `docker-compose.yml` defines no `healthcheck` for either the `python-env` or `ollama-service` containers. Docker and any orchestrator have no way to know if the Ollama model is loaded and ready to serve inference requests. Entrypoints rely on a hardcoded `sleep 5`.

- ❌ **Errors propagate with context sufficient for diagnosis** -- `python/code_review.py` has zero error handling. There are no `try/except` blocks around the HTTP call (line 32), the JSON parsing (line 35), or the dictionary key access (lines 37-48). If the Ollama service returns a non-200 status, a malformed response, or is unreachable, the script will crash with an unhandled exception and a raw Python traceback. There is no error categorization (retryable vs permanent), no request correlation, and no contextual information in any error path.

- ❌ **External calls have explicit timeouts** -- The `requests.post()` call at `python/code_review.py:32` has no timeout. This is also a Hygiene finding (see above).

- ❌ **Logging is structured with request correlation** -- The only output mechanism is `print()` statements (lines 33, 50-55). There is no structured logging (no `logging` module, no JSON output, no log levels). There are no correlation IDs, no timestamps (beyond what the terminal may add), and no way to trace a review request through the system.

---

## Higher Levels -- Preview

> **Level 2 -- Operational Maturity**: SLOs defined and measurable from telemetry; external dependencies have failure isolation; degradation paths exist (partial function over total failure); alert definitions reference response procedures. None of these criteria are present in the current codebase.

> **Level 3 -- Excellence**: Deployment can proceed without downtime; capacity limits enforced under load; failure scenarios codified as automated tests; resource consumption bounded and observable. No CI/CD pipeline (`.github/` directory is absent), no tests exist, no capacity controls, no resource bounding.

---

## Detailed Findings

| Priority | Severity | Maturity | Category | Location | Finding | Recommendation |
|----------|----------|----------|----------|----------|---------|----------------|
| 1 | HIGH | HYG | Excessive Latency | `python/code_review.py:32` | No timeout on `requests.post()` -- caller blocks indefinitely if Ollama is unresponsive | Add `timeout=(5, 300)` parameter to `requests.post()` |
| 2 | HIGH | HYG | Misconfiguration | `.devcontainer/entrypoint.*.sh:9` | Hardcoded `sleep 5` readiness gate; Ollama may not be ready, causing silent failures | Replace with a polling readiness loop against the Ollama HTTP endpoint |
| 3 | HIGH | L1 | Fault Isolation | `python/code_review.py:32-48` | No error handling whatsoever -- unhandled exceptions crash the process with raw tracebacks | Wrap HTTP call and response parsing in `try/except` with specific exception types (`requests.ConnectionError`, `requests.Timeout`, `KeyError`, `json.JSONDecodeError`) |
| 4 | HIGH | L1 | Availability | `docker-compose.yml` | No `healthcheck` directive on `ollama-service`. Docker has no way to detect if the model is loaded and ready | Add a `healthcheck` section: `test: ["CMD", "curl", "-f", "http://localhost:11434/"]`, with `interval`, `timeout`, `retries` |
| 5 | MEDIUM | L1 | Misconfiguration | `python/code_review.py:7` | Ollama service URL is hardcoded as `http://ollama-service:11434/api/chat`. No environment variable override, no config validation | Read URL from an environment variable with a sensible default: `os.environ.get("OLLAMA_URL", "http://ollama-service:11434/api/chat")` |
| 6 | MEDIUM | L1 | Misconfiguration | `python/code_review.py:26` | Model name `deepseek-r1:14b` is hardcoded; other Dockerfiles provision different model sizes (1.5b, 32b, 70b, 671b) | Make model name configurable via environment variable |
| 7 | MEDIUM | L1 | Observability | `python/code_review.py:33,50-55` | All output is via `print()` -- no structured logging, no log levels, no correlation IDs | Replace `print()` with Python `logging` module using structured JSON output |
| 8 | MEDIUM | L1 | Fault Isolation | `python/code_review.py:35-48` | Response JSON is accessed without any validation -- if Ollama returns an unexpected schema (e.g. error response), multiple `KeyError` exceptions cascade | Validate response status code before parsing; validate expected keys exist in JSON payload |
| 9 | MEDIUM | L2 | Capacity | `.devcontainer/docker-compose.yml:24-29` | `ollama-service` reserves all GPUs (`count: all`) with no memory limits or CPU constraints defined. No resource limits on `python-env` either | Define explicit `mem_limit`, `cpus` constraints on both services. Consider limiting GPU allocation |
| 10 | MEDIUM | L2 | Redundancy | `docker-compose.yml:14-17` | Single Ollama service instance with no replica count, no restart policy. If the container crashes, it stays down | Add `restart: unless-stopped` or `restart: on-failure` policy to `ollama-service` |
| 11 | LOW | L1 | Misconfiguration | `.devcontainer/requirements.txt` | Dependencies (`boto3`, `python-dotenv`, `requests`) are unpinned -- no version constraints. Builds are not reproducible; a breaking upstream release could silently break the tool | Pin dependencies to specific versions or use a lockfile (e.g. `pip freeze > requirements.txt` or use `pip-tools`) |
| 12 | LOW | L1 | Misconfiguration | `.devcontainer/deepseek-r1.001.5b.dockerfile:19` | Dockerfile is missing `COPY ./entrypoint.001.5b.sh /entrypoint.sh` and the container has no entrypoint defined (unlike the 14b/32b/70b/671b variants) | Add the `COPY` and `ENTRYPOINT` instructions to match the other Dockerfiles |
| 13 | LOW | L2 | Observability | `docker-compose.yml` | No log driver configuration; container logs go to default JSON file driver with no rotation. Could fill disk in long-running environments | Configure `logging` options with `max-size` and `max-file` in docker-compose |
| 14 | LOW | L3 | Availability | project root | No CI/CD pipeline (`.github/workflows/` absent). No automated tests. No linting or type checking configured | Add GitHub Actions workflow with at minimum: lint, type-check, and a smoke test that validates the Python script can be imported |
| 15 | LOW | L3 | Output Correctness | `python/code_review.py` | The `python-dotenv` and `boto3` packages are listed in `requirements.txt` but never used in the code. Unused dependencies increase attack surface and container image size | Remove unused dependencies from `requirements.txt` or add the code that uses them |

---

## What's Good

- **Framework-driven review system**: The prompt architecture in `.claude/prompts/sre/` is well-structured. The ROAD framework (Response, Observability, Availability, Delivery) combined with SEEMS/FaCTOR provides comprehensive coverage. Each pillar has a detailed checklist with anti-patterns, which is exactly what mature incident prevention looks like at the design level.

- **Maturity model with Hygiene gate**: The cascading maturity model (HYG > L1 > L2 > L3) with the Irreversible/Total/Regulated hygiene tests is a strong pattern. It ensures the most damaging issues surface first, regardless of which maturity level they belong to.

- **Multiple model size options**: The provision of 5 different model sizes (1.5b through 671b) via separate Dockerfiles gives operators flexibility to trade off quality vs. resource consumption. This is a practical operational consideration.

- **Network isolation**: The `docker-compose.yml` uses a dedicated `llm-network` bridge network, providing basic network isolation between the LLM service and external systems.

- **GPU-aware deployment**: The docker-compose configuration properly reserves GPU resources via the NVIDIA runtime configuration, which is necessary for practical LLM inference performance.

- **Separation of concerns**: The prompt library (`.claude/prompts/`) is cleanly separated from the agent definitions (`.claude/agents/`), skill orchestrators (`.claude/skills/`), and infrastructure (`.devcontainer/`). This makes the system modular and each piece independently evolvable.
