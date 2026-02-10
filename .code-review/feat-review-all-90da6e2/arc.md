# Architecture Review -- Maturity Assessment

## Maturity Status

| Level | Status | Summary |
|-------|--------|---------|
| Hygiene | ⚠️ | Hardcoded service URL in production-callable Python code; large embedded SQL with production database references committed to repository |
| Level 1 -- Foundations | ❌ | Module boundaries are not defined; no public interfaces, no dependency inversion, no isolation for testing |
| Level 2 -- Operational Maturity | 🔒 | Locked -- Level 1 not passed |
| Level 3 -- Excellence | 🔒 | Locked -- Level 2 not passed |

**Immediate Action:** Extract the hardcoded Ollama service URL (`http://ollama-service:11434`) from `python/code_review.py` into environment configuration, and remove the embedded production SQL containing real database schema names (`CHU_PROD`, `LLS_PROD`, `POK_PROD`, `CAM_PROD`) from the committed Python source.

---

## Hygiene

| Severity | Maturity | Zoom Level | Location | Finding | Recommendation |
|----------|----------|------------|----------|---------|----------------|
| HIGH | HYG | Code | `python/code_review.py:7` | **Hardcoded infrastructure URL** -- The Ollama API endpoint `http://ollama-service:11434/api/chat` is hardcoded directly in the function body. If this service is redeployed to a different host or port, the code must be modified. This is a deployment coupling that could cause total failure of the review engine if the hostname changes. | Extract to an environment variable (e.g., `OLLAMA_URL`) with a sensible default. Load via `os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")`. |
| HIGH | HYG | Code | `python/code_review.py:132-500` | **Production database schema names embedded in source code** -- The `get_code_for_review()` function returns a hardcoded SQL string containing real production schema references: `CHU_PROD.CURATED.FACT_CHUMBA_PLAYS`, `LLS_PROD.CURATED.plays`, `POK_PROD.CURATED.V_UNIFIED_PLAYS`, `CAM_PROD.CURATED.ACCOUNT_VALUE_TIER_DAILY`, etc. These production database identifiers are committed to a public/shared repository. This leaks internal infrastructure topology. | Move sample SQL to external fixture files (e.g., `samples/big_winners.sql`). If the SQL is sample input for testing the review tool, load it from disk at runtime rather than embedding it in source. |
| MEDIUM | HYG | Code | `python/code_review.py:32` | **No timeout on HTTP call to Ollama** -- `requests.post(url, json=payload)` has no timeout parameter. If the Ollama service hangs (which is plausible for large model inference), the calling process blocks indefinitely. This is the "unprotected integration point" anti-pattern from Release It! that can cause total unavailability. | Add explicit connect and read timeouts: `requests.post(url, json=payload, timeout=(5, 300))`. |

---

## Level 1 -- Foundations -- Detailed Assessment

- ❌ **Module boundaries are explicit with defined public interfaces** -- Missing. The entire Python runtime code is a single file (`python/code_review.py`) with four flat functions and no module structure. There are no packages, no `__init__.py`, no separation of concerns between "Ollama client," "prompt construction," and "sample data." The `.claude/` directory is well-organized into `prompts/`, `agents/`, `skills/`, and `commands/`, but this organization exists only in markdown configuration, not in executable code.

- ❌ **Dependencies flow inward (infrastructure depends on domain, not vice versa)** -- Missing. `python/code_review.py` mixes all concerns in one file: HTTP client infrastructure (`requests.post`), prompt construction logic (the `get_context`, `get_planning_rules`, `get_format_rules` functions), and sample data (`get_code_for_review`). There is no domain layer, no application layer, and no inward dependency flow. The `review_code()` function directly constructs the HTTP payload, makes the request, and parses the response -- all in one function.

- ❌ **Components can be tested in isolation** -- Missing. No test files exist anywhere in the repository. The `review_code()` function cannot be tested without a live Ollama service running (the URL is hardcoded, there is no dependency injection, and the HTTP call is inline). There is no way to mock or stub the LLM backend. The `get_code_for_review()` function returns a 400-line hardcoded string, making it impossible to test the review tool against different inputs without modifying source.

---

## Higher Levels -- Preview

> **Level 2 -- Operational Maturity**: Integration contracts between the Python client and Ollama API are not defined or validated. No ADRs document design decisions (e.g., why DeepSeek R1, why the specific prompt structure, why XML-style tags for prompt formatting). Error handling at the Ollama integration point does not exist -- no retry logic, no circuit breaker, no graceful degradation if the model is unavailable. The docker-compose configuration has no health checks.

> **Level 3 -- Excellence**: No architectural fitness functions exist in CI. No automated tests validate that the prompt template structure in `.claude/prompts/` follows the expected format. No dependency governance validates that new prompts conform to the maturity model structure. No contract tests verify Ollama API compatibility across versions.

---

## Detailed Findings

| Priority | Severity | Maturity | Zoom Level | Location | Finding | Recommendation |
|----------|----------|----------|------------|----------|---------|----------------|
| 1 | HIGH | HYG | Code | `python/code_review.py:7` | Hardcoded Ollama URL `http://ollama-service:11434/api/chat` creates deployment coupling. Hostname change = total failure. | Use `os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")` |
| 2 | HIGH | HYG | Code | `python/code_review.py:132-500` | Production database schema names (`CHU_PROD`, `LLS_PROD`, `POK_PROD`, `CAM_PROD`) embedded as string literals in committed source code. Leaks internal data infrastructure topology. | Extract SQL samples to external fixture files under `samples/` or `tests/fixtures/` |
| 3 | MEDIUM | HYG | System | `python/code_review.py:32` | HTTP POST to Ollama has no timeout. Model inference can take minutes; if Ollama hangs, the client blocks forever. Unprotected integration point (Release It! anti-pattern). | Add `timeout=(5, 300)` to `requests.post()` |
| 4 | HIGH | L1 | Code | `python/code_review.py` (entire file) | **God module** -- Single 503-line file containing HTTP client logic, prompt construction, format rules, and a 370-line embedded SQL sample. Violates SRP: at least 4 distinct responsibilities in one module. | Split into: `client.py` (Ollama HTTP client), `prompts.py` (prompt construction), `samples/` (external review input files), `main.py` (entry point) |
| 5 | HIGH | L1 | Code | `python/code_review.py:36-53` | **Primitive obsession / stringly-typed data** -- Response parsing extracts 10+ fields from a JSON dict with no data class or typed model. Variables like `model`, `content`, `eval_count` are raw strings/ints with no validation. If the Ollama API changes a field name, failure occurs silently or with an opaque `KeyError`. | Define a `@dataclass` or Pydantic model for the Ollama response structure. Parse response into a typed object at the boundary. |
| 6 | HIGH | L1 | Code | `python/code_review.py:6-56` | **Mixed concerns** -- `review_code()` constructs prompts, builds HTTP payloads, makes HTTP calls, parses responses, and prints output -- all in one function. No separation between orchestration and infrastructure. Impossible to test prompt construction independently of HTTP calls. | Apply Ports & Adapters: define a `ReviewClient` protocol/ABC for the LLM backend, inject it into the review function, and implement `OllamaReviewClient` separately. |
| 7 | HIGH | L1 | Service | `python/code_review.py` | **No test infrastructure** -- Zero test files in the entire repository. No `tests/` directory, no `pytest.ini`, no test configuration. The Python code cannot be verified automatically. The `.claude/` prompt library has no validation that prompt files conform to expected structure. | Add `tests/` directory with at minimum: unit tests for prompt construction, integration test fixture for Ollama client (with mock), and a structural test that validates `.claude/prompts/` files contain required sections. |
| 8 | MEDIUM | L1 | Code | `python/code_review.py:61-112` | **Dead code** -- Lines 61-112 contain large blocks of commented-out code and alternative prompt examples stored as multi-line docstrings that are never used. These are documentation artifacts from experimentation, not functional code. | Move prompt examples to documentation or sample files. Remove dead code blocks from the source file. |
| 9 | MEDIUM | L1 | Code | `python/code_review.py:1-4` | **Unused imports** -- `json`, `datetime`, and `literal_eval` are imported but never used in the module. | Remove unused imports: `json`, `datetime`, `from ast import literal_eval`. |
| 10 | MEDIUM | L1 | Service | `.devcontainer/docker-compose.yml:1` | **Deprecated Compose file format** -- Uses `version: "3.8"` which is deprecated in modern Docker Compose. While not breaking, it signals an outdated configuration. | Remove the `version` key (modern Compose infers the format) or update to current conventions. |
| 11 | MEDIUM | L1 | Service | `.devcontainer/docker-compose.yml:10-30` | **No health check on Ollama service** -- The `ollama-service` in docker-compose has no `healthcheck` directive. The `python-env` service could attempt to call Ollama before the model is loaded. The entrypoint uses `sleep 5` as a timing hack rather than a proper readiness check. | Add a `healthcheck` with `curl --fail http://localhost:11434/api/tags` to the Ollama service definition. Use `depends_on` with `condition: service_healthy` for the Python service. |
| 12 | MEDIUM | L1 | Code | `python/code_review.py:26` | **Hardcoded model name** -- The model `"deepseek-r1:14b"` is hardcoded in the payload. There are separate Dockerfiles for different model sizes but the Python client always requests `14b`. | Make the model name configurable via environment variable or function parameter. |
| 13 | MEDIUM | L2 | Landscape | Repository root | **No ADRs** -- The repository has no `docs/adr/` or equivalent directory. Significant design decisions are undocumented: Why XML-style tags for prompt structure? Why 4 subagents per domain? Why the specific maturity model (Hygiene/L1/L2/L3)? Why DeepSeek R1 for local inference? The `agent-os/specs/` directory contains shape-up style specs, but these are feature shapes, not architecture decision records. | Create an `adr/` directory with lightweight ADRs for key decisions. Start with: ADR-001 (multi-agent review architecture), ADR-002 (maturity model design), ADR-003 (prompt template structure). |
| 14 | MEDIUM | L2 | Landscape | Repository root | **No technical specification** -- There is no `DESIGN.md`, `tech-spec.md`, or architectural overview document that describes the intended system design. The `readme.md` serves as a user guide but does not describe component interactions, data flow, or design constraints. The `agent-os/product/mission.md` describes the problem, not the architecture. | Create a `DESIGN.md` or `docs/architecture.md` covering: component diagram, data flow (prompt template -> subagent -> findings -> synthesis), integration points, and key constraints. |
| 15 | LOW | L1 | Code | `python/code_review.py:117-129` | **Inconsistent function naming** -- Functions `get_context()`, `get_planning_rules()`, `get_format_rules()`, `get_code_for_review()` follow `get_*` naming but return hardcoded strings. These are not getters; they are factory functions or constant providers. The naming misleadingly implies dynamic retrieval. | Rename to constants (e.g., `CONTEXT`, `PLANNING_RULES`) or rename functions to `build_*` to clarify their nature. |
| 16 | LOW | L1 | Service | `.devcontainer/deepseek-r1.014b.dockerfile:4` | **Race condition in Dockerfile** -- `RUN ollama serve & sleep 5 && ollama pull deepseek-r1:14b` uses a fixed 5-second sleep to wait for Ollama to start. On slow machines or CI environments, 5 seconds may not be enough, causing the pull to fail. | Use a retry loop with health check: `until curl -s http://localhost:11434/api/tags; do sleep 1; done` before the pull command. |
| 17 | LOW | L2 | Landscape | `agent-os/standards/index.yml` | **Incomplete standards index** -- All 11 standards entries have `description: Needs description - run /index-standards`. The index was scaffolded but never populated, making it useless for discovery. | Run `/index-standards` to populate descriptions, or manually add meaningful descriptions for each standard. |
| 18 | LOW | L1 | Code | `.gitignore` | **Minimal .gitignore** -- Only ignores `.DS_Store`. Does not ignore Python artifacts (`__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`), IDE files (`.vscode/`, `.idea/`), virtual environments (`venv/`, `.venv/`), or environment files (`.env`). | Extend `.gitignore` with standard Python, IDE, and environment patterns. |

---

## What's Good

1. **Excellent prompt library architecture** -- The `.claude/prompts/` directory is exceptionally well-organized. Each review domain has a `_base.md` with shared framework context and terminology, plus domain-specific checklists. The separation between base context and zoom-level specifics follows the Open/Closed Principle: new review criteria can be added to a level without modifying the base framework.

2. **Clean agent composition pattern** -- The `.claude/agents/` definitions are minimal and focused. Each agent reads from the shared prompt library rather than duplicating content. The `model: sonnet` directive in agent frontmatter shows deliberate technology selection. The agents follow Interface Segregation: each is specialized for one zoom level.

3. **Well-structured skill orchestration** -- The `SKILL.md` files define a clear process (identify scope, run parallel reviews, synthesize) with explicit output format specifications. The `/review-all` skill delegates to domain skills rather than duplicating their logic, demonstrating good composition.

4. **Cascading maturity model** -- The Hygiene -> L1 -> L2 -> L3 model with locking is well-designed. The Hygiene gate uses clear, testable criteria (Irreversible, Total, Regulated). The maturity levels are cumulative and observable, not subjective.

5. **Thoughtful product design** -- The `agent-os/product/` directory shows clear product thinking: `mission.md` identifies the problem and target users, `tech-stack.md` separates cloud and local modes, and `roadmap.md` defines phased delivery. The shape-up specs in `agent-os/specs/` demonstrate disciplined feature scoping with explicit rabbit holes and no-gos.

6. **Dual-mode architecture** -- Supporting both Claude Code (cloud) and Ollama (local/Docker) demonstrates good portability thinking. The prompt templates are LLM-agnostic, which is a form of the Dependency Inversion Principle applied at the system level.

7. **Docker Compose with GPU support** -- The docker-compose file includes GPU reservation for NVIDIA devices, enabling local GPU-accelerated inference. The multiple Dockerfile variants (1.5B through 671B) provide appropriate model size options for different hardware capabilities.
