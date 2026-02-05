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
2. **Deduplicate** - Some issues may be flagged by multiple reviewers
3. **Prioritize** - Sort by severity (HIGH → MEDIUM → LOW)
4. **Summarize** - Provide executive summary

## Output Format

### Executive Summary

Brief overview of the review:
- Files reviewed
- Total findings by severity
- Top concerns

### Findings by Pillar

#### Response
[Findings from sre-response agent]

#### Observability
[Findings from sre-observability agent]

#### Availability
[Findings from sre-availability agent]

#### Delivery
[Findings from sre-delivery agent]

### Consolidated Action Items

| Priority | Finding | Location | Recommendation | Pillar |
|----------|---------|----------|----------------|--------|
| 1 | ... | ... | ... | ... |

### What's Good

Also note positive patterns observed - resilience patterns done well, good observability practices, etc.
