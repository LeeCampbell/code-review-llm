---
name: review-data
description: Comprehensive data code review for Trusted and Timely data products. Covers architecture, engineering, quality, and governance using DAMA DMBOK and Data Mesh principles.
allowed-tools: Task, Read, Glob, Grep
argument-hint: "<path-to-review>"
---

# Data Code Review

Perform a comprehensive data review of: **$ARGUMENTS**

## Framework

This review ensures **Trusted and Timely** data products using principles from:
- **DAMA DMBOK** - Data Management Body of Knowledge
- **Data Mesh** - Domain ownership, data products, interoperability
- **Data Governance for Everyone** - Practical governance principles

## The Four Pillars

| Pillar | Focus | Key Question |
| ------ | ----- | ------------ |
| **Architecture** | Schema, domains, contracts | Is it designed right? |
| **Engineering** | Code quality, logic, performance | Is it built right? |
| **Quality** | Freshness, accuracy, usability | Does it meet expectations? |
| **Governance** | Compliance, lifecycle, ownership | Is it managed right? |

## Process

### Step 1: Identify Scope

First, identify what code needs to be reviewed:

- If `$ARGUMENTS` is a file or directory, review that directly
- If `$ARGUMENTS` is empty or ".", review recent changes (`git diff`) or prompt for scope
- Focus on SQL, Python, dbt models, pipeline definitions, schema files

### Step 2: Run Parallel Reviews

Spawn **4 subagents in parallel** to analyze different aspects:

1. **data-architecture** - Schema design, domain boundaries, data contracts
   - Polysemes and global identifiers
   - Naming conventions and standards
   - Breaking changes and versioning

2. **data-engineering** - Code quality, logic correctness, performance
   - Transformation testing and idempotency
   - Query optimization and CDC
   - Error handling and recovery

3. **data-quality** - Trust, timeliness, documentation
   - Freshness SLOs and monitoring
   - Data validation and constraints
   - Consumer documentation and discoverability

4. **data-governance** - Compliance, lifecycle, ownership
   - PII classification and masking
   - Retention policies and backup
   - Lineage and ownership clarity

Each agent should:

- Read the base framework from `.claude/prompts/donkey-dev/data/_base.md`
- Read their specific checklist from `.claude/prompts/donkey-dev/data/[pillar].md`
- Review the code against their checklist
- Return findings in standard table format

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
# Data Review — Maturity Assessment

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

[If any failures: list them with severity, pillar, location, finding, recommendation]
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

| Priority | Severity | Maturity | Pillar | Location | Finding | Recommendation |
|----------|----------|----------|--------|----------|---------|----------------|

## What's Good

[Positive data patterns observed — well-designed schemas, good testing, clear documentation, proper governance]
```

## Relationship to Other Reviews

| Concern | Data Review | Also Covered By |
| ------- | ----------- | --------------- |
| Freshness SLOs | Quality pillar | SRE Availability |
| Query performance | Engineering pillar | SRE Capacity |
| PII handling | Governance pillar | Security Data-Protection |
| Lineage | Governance pillar | Security Audit-Resilience |

Overlaps are intentional - each review applies its own lens to shared concerns.
