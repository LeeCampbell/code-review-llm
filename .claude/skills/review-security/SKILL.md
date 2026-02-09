---
name: review-security
description: Comprehensive security code review using STRIDE threat modeling (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
allowed-tools: Task, Read, Glob, Grep
argument-hint: "<path-to-review>"
---

# Security Code Review

Perform a comprehensive security review of: **$ARGUMENTS**

## Framework

This review uses **STRIDE** threat modeling combined with **DREAD-lite** severity scoring:

- **S**poofing → Authentication attacks
- **T**ampering → Injection & integrity attacks
- **R**epudiation → Audit & accountability gaps
- **I**nformation Disclosure → Data leaks
- **D**enial of Service → Availability attacks
- **E**levation of Privilege → Authorization attacks

## Process

### Step 1: Identify Scope

First, identify what code needs to be reviewed:

- If `$ARGUMENTS` is a file or directory, review that directly
- If `$ARGUMENTS` is empty or ".", review recent changes (`git diff`) or prompt for scope
- If `$ARGUMENTS` is a PR number, fetch the diff

### Step 2: Run Parallel Reviews

Spawn **4 subagents in parallel** to analyze different threat categories:

1. **security-authn-authz** - Spoofing + Elevation of Privilege
   - Authentication bypass, session management, authorization logic

2. **security-data-protection** - Information Disclosure + Tampering
   - Secrets exposure, encryption, data integrity

3. **security-input-validation** - Tampering (Injection)
   - SQL injection, XSS, command injection, path traversal

4. **security-audit-resilience** - Repudiation + Denial of Service
   - Audit logging, rate limiting, resource bounds

Each agent should:

- Read the base framework from `.claude/prompts/security/_base.md`
- Read their specific checklist from `.claude/prompts/security/[pillar].md`
- Review the code against their checklist
- Return findings meeting the confidence threshold (>50%)

### Step 3: Synthesize Results

After all agents complete:

1. **Collect findings** from all 4 pillars
2. **Apply confidence filter** — Remove findings below 50% confidence
3. **Deduplicate** — Some issues may be flagged by multiple reviewers
4. **Aggregate maturity assessments** — Merge criteria assessments from all subagents into one maturity view
5. **Determine maturity status per level:**
   - All criteria ✅ → `pass` (✅)
   - Mix of ✅ and ❌ → `partial` (⚠️)
   - All criteria ❌ → `fail` (❌)
   - Previous level not passed → `locked` (🔒)
6. **Prioritize** findings by maturity level (HYG first), then severity + confidence (HIGH/HIGH → LOW/MED)

## Output Format

```markdown
# Security Review — Maturity Assessment

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

[If any failures: list them with severity, confidence, STRIDE category, location, finding, recommendation]
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

| Priority | Severity | Maturity | Confidence | STRIDE | Location | Finding | Recommendation |
|----------|----------|----------|------------|--------|----------|---------|----------------|

## What's Good

[Positive security patterns observed — good practices, effective controls, strong coverage areas]
```

## Comparison with Built-in /security-review

This review complements Claude's built-in `/security-review` by:

- Using structured STRIDE threat modeling
- Providing broader coverage (including audit, DoS)
- Working with local Ollama models
- Offering detailed checklists for each category
