---
name: review-all
description: Run all review domains (Architecture, SRE, Security, Data) against a target path. Writes sub-reports and consolidated summary to .code-review/<batch-name>/.
allowed-tools: Task, Read, Glob, Grep, Bash, Write
argument-hint: "<path> [--name <batch-name>] [--domains ARC,SRE,SEC,DAT]"
---

# Batch Code Review

Run all review domains against: **$ARGUMENTS**

## Process

### Step 1: Parse Arguments

Extract from `$ARGUMENTS`:

- `<path>` — **required**, first positional argument (the target to review)
- `--name <batch-name>` — optional, override for batch directory name
- `--domains <list>` — optional, comma-separated domain codes (default: `ARC,SRE,SEC,DAT`)

Normalise domain list to uppercase. Validate each code against allowed set: `ARC`, `SRE`, `SEC`, `DAT`. Reject unknown codes with an error message.

Map domain codes to their review skills:

| Code | Skill | File | Output |
|------|-------|------|--------|
| `ARC` | Architecture | `.claude/skills/donkey-dev/review-arch/SKILL.md` | `arc.md` |
| `SRE` | SRE | `.claude/skills/donkey-dev/review-sre/SKILL.md` | `sre.md` |
| `SEC` | Security | `.claude/skills/donkey-dev/review-security/SKILL.md` | `sec.md` |
| `DAT` | Data | `.claude/skills/donkey-dev/review-data/SKILL.md` | `dat.md` |

### Step 2: Resolve Batch Name

Use Bash to determine batch name in precedence order:

1. `--name` flag if provided → use as-is
2. `git describe --tags --exact-match HEAD 2>/dev/null` → use tag name if on a tag
3. Not on main/master: `git rev-parse --abbrev-ref HEAD` + `-` + `git rev-parse --short HEAD` → e.g. `feature-foo-abc1234`
4. On main/master: ISO date + `-` + short hash → e.g. `2026-02-10-abc1234`

Sanitise batch name: replace `/` with `-`, lowercase.

### Step 3: Create Output Directory

Use Bash:

```bash
mkdir -p .code-review/<batch-name>/
```

### Step 4: Run Domain Reviews in Parallel

Spawn one Task agent per requested domain, **all in parallel** using `subagent_type: general-purpose`:

| Domain | Task Prompt |
|--------|-------------|
| `ARC` | "You are running an architecture review. Read `.claude/skills/donkey-dev/review-arch/SKILL.md` and follow its process exactly against `<path>`. Return the complete report including the Maturity Status table." |
| `SRE` | "You are running an SRE review. Read `.claude/skills/donkey-dev/review-sre/SKILL.md` and follow its process exactly against `<path>`. Return the complete report including the Maturity Status table." |
| `SEC` | "You are running a security review. Read `.claude/skills/donkey-dev/review-security/SKILL.md` and follow its process exactly against `<path>`. Return the complete report including the Maturity Status table." |
| `DAT` | "You are running a data review. Read `.claude/skills/donkey-dev/review-data/SKILL.md` and follow its process exactly against `<path>`. Return the complete report including the Maturity Status table." |

### Step 5: Write Sub-Reports

As each domain Task agent completes, write its report to the output directory:

- `.code-review/<batch-name>/arc.md` — Architecture report
- `.code-review/<batch-name>/sre.md` — SRE report
- `.code-review/<batch-name>/sec.md` — Security report
- `.code-review/<batch-name>/dat.md` — Data report

Only write files for domains that were requested.

### Step 6: Extract Maturity Status

Parse each sub-report's Maturity Status table to extract per-domain status. Look for the table pattern:

```
| Level | Status | Summary |
```

Map status indicators:
- ✅ → `pass`
- ⚠️ → `partial`
- ❌ → `fail`
- 🔒 → `locked`

Extract the maturity status for each level: Hygiene, Level 1, Level 2, Level 3.

Extract the **Immediate Action** line from each report (the line starting with `**Immediate Action:**`).

### Step 7: Build summary.json

Use Bash to get git metadata (`git rev-parse HEAD`, `git rev-parse --short HEAD`, `git rev-parse --abbrev-ref HEAD`), then use the Write tool to create:

```json
{
  "metadata": {
    "timestamp": "<ISO-8601>",
    "commit": "<full-sha>",
    "branch": "<branch-name>",
    "batch_name": "<batch-name>",
    "path": "<reviewed-path>"
  },
  "domains": {
    "ARC": {
      "hygiene": "pass|partial|fail",
      "level1": "pass|partial|fail|locked",
      "level2": "pass|partial|fail|locked",
      "level3": "pass|partial|fail|locked",
      "immediate_action": "..."
    }
  }
}
```

Only include domains that were requested. Write to `.code-review/<batch-name>/summary.json`.

### Step 8: Build summary.md

Generate consolidated summary using the Write tool. Write to `.code-review/<batch-name>/summary.md`:

```markdown
# Code Review Summary — <batch-name>

**Path:** `<path>`
**Date:** <ISO date>
**Commit:** `<short-hash>` on `<branch>`
**Domains:** ARC, SRE, SEC, DAT

## Maturity Overview

| Domain | Hygiene | L1 | L2 | L3 | Immediate Action |
|--------|---------|----|----|----|--------------------|
| [Architecture](arc.md) | ✅ | ✅ | ⚠️ | 🔒 | Fix circular dep... |
| [SRE](sre.md) | ✅ | ✅ | ✅ | ⚠️ | Add timeouts... |
| [Security](sec.md) | ❌ | 🔒 | 🔒 | 🔒 | SQL injection... |
| [Data](dat.md) | ✅ | ❌ | 🔒 | 🔒 | Use standard types... |

## Sub-Reports

- [Architecture Review](arc.md)
- [SRE Review](sre.md)
- [Security Review](sec.md)
- [Data Review](dat.md)
```

Only include rows and links for domains that were requested. Use relative links to sub-reports.

### Step 9: Completion Output

Display to the user:

```
Batch review complete: .code-review/<batch-name>/

  summary.md   — Headline maturity table
  summary.json — Machine-readable status
  arc.md       — Architecture sub-report
  sre.md       — SRE sub-report
  sec.md       — Security sub-report
  dat.md       — Data sub-report
```

Only list files that were actually written.

## Domain Reference

| Code | Full Name | Skill Path |
|------|-----------|------------|
| `ARC` | Architecture | `/donkey-dev:review-arch` |
| `SRE` | SRE | `/donkey-dev:review-sre` |
| `SEC` | Security | `/donkey-dev:review-security` |
| `DAT` | Data | `/donkey-dev:review-data` |

## Relationship to Domain Reviews

This batch orchestrator **delegates to** the 4 domain review skills. It does not duplicate their logic. Changes to individual domain skills are automatically picked up by `/donkey-dev:review-all`.

- **Architecture** (`/donkey-dev:review-arch`): C4 zoom levels — Code, Service, System, Landscape
- **SRE** (`/donkey-dev:review-sre`): ROAD framework — Response, Observability, Availability, Delivery
- **Security** (`/donkey-dev:review-security`): STRIDE threat modeling
- **Data** (`/donkey-dev:review-data`): DAMA DMBOK / Data Mesh pillars
