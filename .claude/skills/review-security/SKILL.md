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
2. **Apply confidence filter** - Remove findings below 50% confidence
3. **Deduplicate** - Some issues may be flagged by multiple reviewers
4. **Prioritize** - Sort by: HIGH confidence + HIGH severity first
5. **Summarize** - Provide executive summary

## Output Format

### Executive Summary

Brief overview of the review:

- Files reviewed
- Total findings by severity and confidence
- Top security concerns
- STRIDE coverage summary

### Findings by Threat Category

#### Authentication & Authorization (Spoofing + Elevation)

[Findings from security-authn-authz agent]

#### Data Protection (Information Disclosure + Tampering)

[Findings from security-data-protection agent]

#### Input Validation (Injection)

[Findings from security-input-validation agent]

#### Audit & Resilience (Repudiation + DoS)

[Findings from security-audit-resilience agent]

### Consolidated Action Items

| Priority | Severity | Confidence | STRIDE | Location | Finding | Recommendation |
| -------- | -------- | ---------- | ------ | -------- | ------- | -------------- |
| 1 | HIGH | HIGH | ... | ... | ... | ... |

### What's Secure

Note positive security patterns observed:

- Good practices already in place
- Effective security controls
- Areas with strong coverage

## Comparison with Built-in /security-review

This review complements Claude's built-in `/security-review` by:

- Using structured STRIDE threat modeling
- Providing broader coverage (including audit, DoS)
- Working with local Ollama models
- Offering detailed checklists for each category
