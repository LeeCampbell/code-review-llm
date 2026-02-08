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
2. **Deduplicate** - Some issues may be flagged by multiple levels
3. **Prioritize** - Sort by severity (HIGH → MEDIUM → LOW)
4. **Summarize** - Provide executive summary

## Output Format

### Executive Summary

Brief overview of the review:

- Files reviewed
- Total findings by severity
- Top concerns across zoom levels
- Which zoom levels are applicable for this project

### Findings by Zoom Level

#### Code (Module Structure)

[Findings from arch-code agent]

#### Service (Deployable Design)

[Findings from arch-service agent]

#### System (Service Interactions)

[Findings from arch-system agent]

#### Landscape (Ecosystem)

[Findings from arch-landscape agent]

### Consolidated Action Items

| Priority | Severity | Zoom Level | Location | Finding | Recommendation |
| -------- | -------- | ---------- | -------- | ------- | -------------- |
| 1 | HIGH | ... | ... | ... | ... |

### What's Good

Note positive architectural patterns observed:

- Clean separation of concerns
- Well-defined bounded contexts
- Proper use of stability patterns
- Good documentation and ADRs

## Relationship to Other Reviews

This architecture review focuses on **design-time decisions**. It complements:

- **SRE Review** (`/review-sre`): Focuses on run-time reliability
- **Security Review** (`/review-security`): Focuses on threat modeling
- **Data Review** (`/review-data`): Focuses on data products and governance
