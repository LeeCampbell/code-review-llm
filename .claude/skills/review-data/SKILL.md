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

- Read the base framework from `.claude/prompts/data/_base.md`
- Read their specific checklist from `.claude/prompts/data/[pillar].md`
- Review the code against their checklist
- Return findings in standard table format

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
- Top concerns across pillars

### Findings by Pillar

#### Architecture (Schema & Design)

[Findings from data-architecture agent]

#### Engineering (Logic & Code)

[Findings from data-engineering agent]

#### Quality (Trust & Timeliness)

[Findings from data-quality agent]

#### Governance (Compliance & Lifecycle)

[Findings from data-governance agent]

### Consolidated Action Items

| Priority | Severity | Pillar | Location | Finding | Recommendation |
| -------- | -------- | ------ | -------- | ------- | -------------- |
| 1 | HIGH | ... | ... | ... | ... |

### What's Good

Note positive patterns observed:

- Well-designed schemas
- Good testing coverage
- Clear documentation
- Proper governance controls

## Relationship to Other Reviews

| Concern | Data Review | Also Covered By |
| ------- | ----------- | --------------- |
| Freshness SLOs | Quality pillar | SRE Availability |
| Query performance | Engineering pillar | SRE Capacity |
| PII handling | Governance pillar | Security Data-Protection |
| Lineage | Governance pillar | Security Audit-Resilience |

Overlaps are intentional - each review applies its own lens to shared concerns.
