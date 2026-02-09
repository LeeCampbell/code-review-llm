---
name: review-arch
description: Comprehensive architecture code review using C4-inspired zoom levels (Code, Service, System, Landscape). Draws from DDD, Modern Software Engineering, Release It!, and Enterprise Integration Patterns.
allowed-tools: Task, Read, Glob, Grep
argument-hint: "<path-to-review>"
---

# Architecture Code Review

Perform a comprehensive architecture review of: **$ARGUMENTS**

## Framework

This review uses **C4-inspired zoom levels** to evaluate architecture from code structure through to ecosystem integration:

```
Landscape  ─── Between systems      ─── EIP, Context Maps, ADRs
  System   ─── Between services     ─── Release It!, API Contracts
  Service  ─── Inside a deployable  ─── DDD, Clean Architecture
  Code     ─── Inside a module      ─── SOLID, Testability
```

## Process

### Step 1: Identify Scope

First, identify what code needs to be reviewed:

- If `$ARGUMENTS` is a file or directory, review that directly
- If `$ARGUMENTS` is empty or ".", review recent changes (`git diff`) or prompt for scope
- Determine which zoom levels are relevant (monolith may only need Code + Service)

### Step 2: Run Parallel Reviews

Spawn **4 subagents in parallel** to analyze different zoom levels:

1. **arch-code** - Code & Component level
   - SOLID principles, DDD tactical patterns, testability, coupling

2. **arch-service** - Service / Application level
   - Bounded context design, layering, deployability, error model

3. **arch-system** - System level (inter-service)
   - Stability patterns (Release It!), API contracts, service coupling

4. **arch-landscape** - Landscape level (system of systems)
   - Enterprise Integration Patterns, context maps, ADRs, fitness functions

Each agent should:

- Read the base framework from `.claude/prompts/architecture/_base.md`
- Read their specific checklist from `.claude/prompts/architecture/[level].md`
- Review the code against their checklist
- Return findings in standard table format
- Note: Landscape level may return "no findings" for smaller projects - this is expected

### Step 3: Synthesize Results

After all agents complete:

1. **Collect findings** from all 4 zoom levels
2. **Deduplicate** — Some issues may be flagged by multiple levels
3. **Aggregate maturity assessments** — Merge criteria assessments from all subagents into one maturity view
4. **Determine maturity status per level:**
   - All criteria ✅ → `pass` (✅)
   - Mix of ✅ and ❌ → `partial` (⚠️)
   - All criteria ❌ → `fail` (❌)
   - Previous level not passed → `locked` (🔒)
5. **Prioritize** findings by maturity level (HYG first), then severity (HIGH → LOW)

## Output Format

```markdown
# Architecture Review — Maturity Assessment

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

[If any failures: list them with severity, zoom level, location, finding, recommendation]
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

| Priority | Severity | Maturity | Zoom Level | Location | Finding | Recommendation |
|----------|----------|----------|------------|----------|---------|----------------|

## What's Good

[Positive architectural patterns observed]
```

## Relationship to Other Reviews

This architecture review focuses on **design-time decisions**. It complements:

- **SRE Review** (`/review-sre`): Focuses on run-time reliability
- **Security Review** (`/review-security`): Focuses on threat modeling
- **Data Review** (`/review-data`): Focuses on data products and governance
