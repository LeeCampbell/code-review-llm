---
name: review-sre
description: Comprehensive SRE code review using the ROAD framework (Response, Observability, Availability, Delivery) combined with SEEMS/FaCTOR failure analysis
allowed-tools: Task, Read, Glob, Grep
argument-hint: "<path-to-review>"
---

# SRE Code Review

Perform a comprehensive SRE review of: **$ARGUMENTS**

## Framework

This review uses the **ROAD** framework (Response, Observability, Availability, Delivery) combined with **SEEMS** (failure categories) and **FaCTOR** (resilience properties).

## Process

### Step 1: Identify Scope

First, identify what code needs to be reviewed:
- If `$ARGUMENTS` is a file or directory, review that directly
- If `$ARGUMENTS` is empty or ".", review recent changes (`git diff`) or prompt for scope
- If `$ARGUMENTS` is a PR number, fetch the diff

### Step 2: Run Parallel Reviews

Spawn **4 subagents in parallel** to review different aspects:

1. **sre-response** - Incident handling, error messages, runbook readiness
2. **sre-observability** - Logging, metrics, tracing, SLI derivability
3. **sre-availability** - SLOs, circuit breakers, resilience patterns
4. **sre-delivery** - Deployment safety, rollback, feature flags

Each agent should:
- Read the relevant prompt from `.claude/prompts/sre/`
- Review the code against their checklist
- Return findings in table format

### Step 3: Synthesize Results

After all agents complete:

1. **Collect findings** from all 4 pillars
2. **Deduplicate** — Some issues may be flagged by multiple reviewers
3. **Aggregate maturity assessments** — Merge criteria assessments from all subagents into one maturity view
4. **Determine maturity status per level:**
   - All criteria ✅ → `pass` (✅)
   - Mix of ✅ and ❌ → `partial` (⚠️)
   - All criteria ❌ → `fail` (❌)
   - Previous level not passed → `locked` (🔒)
5. **Prioritize** findings by maturity level (HYG first), then severity (HIGH → LOW)

## Output Format

```markdown
# SRE Review — Maturity Assessment

## Maturity Status

| Level | Status | Summary |
|-------|--------|---------|
| Hygiene | ✅/⚠️/❌ | [one-line summary] |
| Level 1 — Foundations | ✅/⚠️/❌/🔒 | [one-line summary] |
| Level 2 — Operational Maturity | ✅/⚠️/❌/🔒 | [one-line summary] |
| Level 3 — Excellence | ✅/⚠️/❌/🔒 | [one-line summary] |

**Immediate Action:** [Top hygiene failure if hygiene not passed, else top action from next achievable level]

---

## Hygiene

[If any failures: list them with severity, category, location, finding, recommendation]
[If all pass: ✅ All hygiene criteria met]

## [Next Achievable Level] — Detailed Assessment

For each criterion:
- ✅ **[Criterion]** — Evidence: `file:line` description
- ❌ **[Criterion]** — Missing: what should exist
- ⚠️ **[Criterion]** — Partial: what's there and what's missing

## Higher Levels — Preview

> **Level [N+1]**: [Brief list of criteria — not yet assessed in detail]
> **Level [N+2]**: [Brief list of criteria]

---

## Detailed Findings

| Priority | Severity | Maturity | Category | Location | Finding | Recommendation |
|----------|----------|----------|----------|----------|---------|----------------|

## What's Good

[Positive SRE patterns observed — resilience patterns done well, good observability practices, etc.]
```
