# Data Review -- Maturity Assessment

## Maturity Status

| Level | Status | Summary |
|-------|--------|---------|
| Hygiene | ❌ | PII exposure in embedded SQL (USER_ID, player addresses) with no masking; known data-loss bug documented but unfixed |
| Level 1 -- Foundations | 🔒 | Hygiene not passed; schemas undocumented, no field descriptions, no input validation, no idempotency guarantees |
| Level 2 -- Operational Maturity | 🔒 | Hygiene not passed; no freshness SLOs, no data contracts, no lineage tracking, no reconciliation |
| Level 3 -- Excellence | 🔒 | Hygiene not passed; no bitemporality, no discoverability, no automated reconciliation |

**Immediate Action:** Fix the documented data-loss bug in the big-win threshold filter (`python/code_review.py:155,170`) where wins spread across multiple spins are silently missed, and implement PII masking for USER_ID and address data in the embedded SQL and stored result outputs.

---

## Hygiene

The following findings trigger the Hygiene gate:

| # | Test | Finding | Location |
|---|------|---------|----------|
| 1 | **Regulated** | USER_ID (player identifiers), STATE (address subdivision codes), and account contact addresses are processed and output with zero masking or classification. In gaming/sweepstakes, player identity combined with financial win amounts constitutes PII under multiple regulatory frameworks (GDPR, state gaming regulations). | `python/code_review.py:132-498` (embedded SQL), `results/001-sql code-r1-1.5b/output.txt`, `results/002-sql-code-r1-14b/output.txt` |
| 2 | **Irreversible** | Known data-loss bug is documented in comments but not fixed: `--BUG: Wouldn't find plays that won 10k over multiple spins for the same play i.e. 2k+4k+5k`. The filter `WIN_AMOUNT / 100 >= 100000` applies per-spin, not aggregated per-play, silently dropping qualifying wins. This means financial reporting for big-win events is incomplete -- once reports are consumed downstream, the missing records cannot be retroactively corrected in consumers' systems. | `python/code_review.py:153-155`, `python/code_review.py:169-170` |
| 3 | **Regulated** | LLM review results stored in `results/` contain the full production SQL with database names (`CHU_PROD`, `LLS_PROD`, `POK_PROD`, `CAM_PROD`), schema names, table structures, and column names -- effectively a map of the production data warehouse. This is committed to a Git repository with no access controls or classification. | `results/001-sql code-r1-1.5b/input.txt`, `results/002-sql-code-r1-14b/input.txt` |
| 4 | **Irreversible** | The Python client (`code_review.py`) has no error handling. If the Ollama API call fails, `response.json()` throws an unhandled exception. More critically, if the API returns a partial or malformed response, the code will crash with no logging, losing the review output entirely. Combined with `"stream": False`, a long-running review that fails at the end loses all work. | `python/code_review.py:32-54` |

---

## Level 1 -- Foundations -- Detailed Assessment

> Note: Hygiene gate is not passed, so L1 is locked. Assessment below is provided for planning purposes.

- ❌ **Schemas are documented with field-level descriptions** -- The embedded SQL in `python/code_review.py` references dozens of tables and columns (`FACT_CHUMBA_PLAYS`, `DIM_GAME`, `DIM_PLAYER`, `ACCOUNT_VALUE_TIER_DAILY`, etc.) with no field-level documentation. Column semantics are conveyed only through inline comments (e.g., `-- Sum because we want to see the initial play amt even if player won on free spin`). There is no schema documentation file, no dbt `schema.yml`, no data dictionary.

- ❌ **Each data asset has a defined owner** -- No ownership is declared anywhere in the repository. The `agent-os/standards/index.yml` has placeholder descriptions (`Needs description - run /index-standards`). There is no CODEOWNERS file, no ownership metadata in the SQL or Python files, no catalog registration.

- ❌ **Input data is validated (types, constraints, referential integrity)** -- The embedded SQL performs no input validation. There are no NOT NULL checks, no constraint enforcement, no referential integrity verification. The extensive use of `CAST(... AS STRING)` throughout the joins (e.g., `cast(d.USER_ID AS STRING) = cast(avtd.ACCOUNT_ID AS STRING)` at line 187) suggests type mismatches between source tables that are papered over rather than validated. The `ifnull(play_id, player_id)` pattern at line 243 silently substitutes a different identifier when the primary one is missing, with no logging or alerting.

- ❌ **Processing is idempotent -- re-runs produce identical results** -- The SQL is a read-only query (SELECT only), which is inherently idempotent for a point-in-time read. However, there is no mechanism to ensure consistent results across runs -- no snapshot isolation, no watermarking, no partition pinning. The query uses `>= '2024-01-01'` as a hardcoded date filter, meaning the result set grows unboundedly over time. There is no evidence of how this query is orchestrated or whether re-runs are expected to produce the same output.

---

## Higher Levels -- Preview

> **Level 2 -- Operational Maturity**: Freshness SLOs defined and monitored. Data contracts between producers and consumers. Source-to-destination lineage. Automated quality checks. Source-target reconciliation.

> **Level 3 -- Excellence**: Temporal change tracking for audit-critical data (bitemporality). Data assets discoverable without tribal knowledge. Automated reconciliation with alerting on divergence.

---

## Detailed Findings

| Priority | Severity | Maturity | Pillar | Location | Finding | Recommendation |
|----------|----------|----------|--------|----------|---------|----------------|
| 1 | HIGH | HYG | Governance | `python/code_review.py:132-498` | **Unmasked PII in output**: USER_ID, STATE (address subdivision), and account contact details flow through to final output with no masking, hashing, or classification. Gaming win amounts combined with player identity is regulated data. | Classify all columns by sensitivity. Hash or tokenize USER_ID in analytical outputs. Mask STATE to region-level if full subdivision is not required. Add data classification comments to the SQL. |
| 2 | HIGH | HYG | Engineering | `python/code_review.py:153-155,169-170` | **Known data-loss bug left unfixed**: Comments document that the `WIN_AMOUNT / 100 >= 100000` filter misses wins split across multiple spins. This is a correctness bug in financial reporting for big-win events. | Replace per-spin filtering with an aggregated approach: use a subquery that `SUM(WIN_AMOUNT)` grouped by `PLAY_ID` before applying the threshold filter. Remove the bug comments once fixed. |
| 3 | HIGH | HYG | Governance | `results/*/input.txt` | **Production database schema committed to Git**: Full production SQL with database names, schema names, table structures, and column names is stored in version control with no access restrictions. | Remove the `results/` directory from Git history using `git filter-branch` or BFG Repo Cleaner. Add `results/` to `.gitignore`. Store review outputs in a secure, access-controlled location. |
| 4 | HIGH | HYG | Engineering | `python/code_review.py:32-54` | **No error handling in API client**: The Ollama API call has no try/except, no timeout, no retry logic. A failed HTTP request or malformed JSON response crashes the process with no recovery. | Wrap the API call in try/except with logging. Add a `timeout` parameter to `requests.post()`. Implement retry with exponential backoff. Handle partial responses gracefully. |
| 5 | HIGH | L1 | Architecture | `python/code_review.py:183-196` | **Tight cross-domain coupling**: The SQL joins across 4 production database domains (`CHU_PROD`, `LLS_PROD`, `POK_PROD`, `CAM_PROD`) via direct table references. Any schema change in any domain breaks this query. | Consume from published data contracts or views rather than internal tables. Define explicit interfaces between domains. |
| 6 | HIGH | L1 | Engineering | `python/code_review.py:187,266,321-322,443-445,462-464,483` | **Excessive CAST(... AS STRING) in join conditions**: Over 20 instances of `cast(X AS STRING) = cast(Y AS STRING)` in join conditions. This defeats index usage, creates implicit type coercion risks, and masks underlying type mismatches between tables. | Fix the source type mismatches at the schema level. If cross-domain joins require type alignment, standardize on a single type (preferably the native key type) and cast once in a staging layer, not in every join. |
| 7 | HIGH | L1 | Engineering | `python/code_review.py:132-498` | **Entire SQL query embedded as a Python string literal**: A 370-line production SQL query is hardcoded inside a Python function as a string return value. This is untestable, unversionable (as SQL), and impossible to lint or validate. | Extract the SQL to a separate `.sql` file. Load it at runtime. This enables SQL linting, version diffing, and independent testing. |
| 8 | MEDIUM | L1 | Architecture | `python/code_review.py:141-498` | **Massive duplicated CTE patterns across brands**: The CHU, LLS, and POK winner CTEs follow nearly identical patterns but with different table/column names. This is copy-paste code that will diverge over time. | Extract a parameterized template or macro (e.g., dbt macro, Jinja template) that generates brand-specific CTEs from a configuration table, eliminating duplication. |
| 9 | MEDIUM | L1 | Quality | `python/code_review.py:132-498` | **No field-level documentation**: Columns like `COIN_TYPE_KEY = 2`, `CURRENCY_TYPE = 'sweeps'`, magic number `100` (divisor for amount conversion), and `100000` (big-win threshold) have no documentation beyond sparse inline comments. | Add a data dictionary defining each column, its business meaning, valid values, and units. Document the magic numbers as named constants or configuration. |
| 10 | MEDIUM | L1 | Quality | `python/code_review.py:151,167,198,232,249,276,280,334,342` | **Hardcoded date filter `>= '2024-01-01'`**: The same date appears 9 times across the query with no parameterization. If the reporting window needs to change, all 9 instances must be updated manually. | Extract the date to a parameter or variable. Pass it as a query parameter from the Python caller. |
| 11 | MEDIUM | L1 | Engineering | `python/code_review.py:1-4` | **Unused imports**: `json`, `datetime`, and `literal_eval` from `ast` are imported but never used in the code. | Remove unused imports to improve code clarity. |
| 12 | MEDIUM | L2 | Quality | Entire repository | **No freshness SLO defined**: There is no documented expectation for when this big-win data should be available. No monitoring, no alerting on late delivery. | Define a freshness SLO (e.g., "big-win data available within 4 hours of event"). Implement freshness monitoring. |
| 13 | MEDIUM | L2 | Quality | Entire repository | **No reconciliation mechanism**: There is no way to verify the query output matches the source systems. No row count checks, no sum verification, no sample validation. | Add reconciliation checks: compare output row counts and sum of `SC_WIN_AMOUNT` against source system totals. |
| 14 | MEDIUM | L2 | Governance | Entire repository | **No data lineage captured**: The transformation from source tables to `winners_final` is only documented implicitly in the SQL. There is no lineage metadata, no DAG definition, no catalog entry. | Register this query as a data asset with explicit lineage (input tables, transformation logic, output schema). Use a tool like dbt, DataHub, or Amundsen. |
| 15 | MEDIUM | L2 | Governance | Entire repository | **No retention or lifecycle policy**: There is no indication of how long the output data is retained, whether old results are archived or purged, or what the backup strategy is. The `results/` directory accumulates outputs with no lifecycle management. | Define retention policies for both the query output and the stored review results. |
| 16 | LOW | L1 | Architecture | `python/code_review.py:132-498` | **Inconsistent naming conventions**: The SQL mixes `UPPER_SNAKE` for most columns, `lower_snake` for CTE names, and quoted `"PascalCase"` in the final SELECT. Column aliasing is inconsistent (`AS DATE` vs `AS user_id` at line 473). | Standardize on a single naming convention (preferably `snake_case` throughout) and apply consistently. |
| 17 | LOW | L1 | Engineering | `python/code_review.py:61-112` | **Dead code in docstrings**: Multiple commented-out code blocks and unused docstring examples remain in the `review_code()` function body, including curl examples and product launch email templates that are unrelated to data review. | Remove dead code and unrelated examples. Keep only relevant documentation. |
| 18 | LOW | L1 | Engineering | `.devcontainer/docker-compose.yml:1` | **Deprecated docker-compose version key**: `version: "3.8"` is deprecated in modern Docker Compose and generates warnings. | Remove the `version` key entirely; modern Docker Compose infers the version automatically. |
| 19 | LOW | L1 | Quality | `agent-os/standards/index.yml` | **Standards index unpopulated**: All 11 standard entries have placeholder descriptions (`Needs description - run /index-standards`). This reduces discoverability. | Run `/index-standards` or manually populate the descriptions for each standard. |

---

## What's Good

- **Well-structured review framework**: The `.claude/prompts/data/` directory contains a thorough, well-organized review framework across all four pillars (Architecture, Engineering, Quality, Governance). The base framework in `_base.md` provides clear terminology, severity definitions, and a cascading maturity model.

- **Clear product vision**: The `agent-os/product/mission.md` and `roadmap.md` articulate a strong product vision for multi-perspective code reviews with clear phases and priorities.

- **Modular agent architecture**: The separation of concerns between skills (orchestrators), agents (subagent definitions), and prompts (checklists) is clean and extensible. Adding a new review domain follows a clear pattern.

- **CTE-based SQL structure**: The embedded SQL uses Common Table Expressions effectively to decompose a complex multi-brand aggregation into readable, named steps. The CTE names (`chu_recent_inhouse_big_win_plays`, `player_state`, `winners_final`) convey intent.

- **Inline comments where present**: Where comments exist in the SQL (e.g., `-- Tier at the time player won`, `-- Sum because we want to see the initial play amt even if player won on free spin`), they explain business intent rather than restating the code. The bug documentation, while flagging an unfixed issue, demonstrates awareness of correctness concerns.

- **LLM-agnostic prompt design**: The prompt library in `.claude/prompts/` is designed to work across different LLMs (Claude Code cloud, Ollama local), with the framework documentation separated from the orchestration logic.

- **Practical Docker setup**: The `.devcontainer/` directory provides a working Docker Compose setup with multiple model size options, making it straightforward to run local reviews on different hardware configurations.
