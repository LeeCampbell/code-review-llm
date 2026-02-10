# Shape: Batch Review Command (`/review-all`)

## Problem

The 4 domain review skills (`/review-arch`, `/review-sre`, `/review-security`, `/review-data`) each produce standalone maturity assessments written to stdout. There is no way to run all domains at once, compare maturity across domains, or persist results to disk for tracking over time.

## Appetite

Small batch — 1 new SKILL.md file. No modifications to existing skills or prompts.

## Solution

Add `/review-all` — a batch orchestrator that:

1. Runs all (or selected) domain reviews against a target path
2. Writes sub-reports and a consolidated summary to `.code-review/<batch-name>/`
3. Produces both human-readable (`summary.md`) and machine-readable (`summary.json`) outputs

The skill delegates to existing domain skills via Task agents rather than directly spawning 16 subagents. Each Task agent reads and follows the relevant SKILL.md, so review-all automatically benefits from improvements to individual skills.

## Key Decisions

- **Delegation over duplication**: Each domain review is run by a general-purpose Task agent that follows the existing SKILL.md. No synthesis logic is duplicated.
- **Batch naming**: Automatic naming from git state (tag → branch-hash → date-hash) with `--name` override.
- **Domain filtering**: `--domains ARC,SRE,SEC,DAT` flag to run a subset. Default is all four.
- **Output location**: `.code-review/<batch-name>/` — easily gitignored or committed as desired.
- **Dual output**: `summary.md` for humans, `summary.json` for tooling/CI integration.

## Rabbit Holes

- **Auto-committing results**: Not in scope. Users decide whether to commit `.code-review/` output.
- **CI integration**: Future work. The `summary.json` format is designed for it but no CI hooks are added.
- **Trend analysis**: Comparing batch results over time is a future feature that builds on the JSON output.
- **Custom domain order**: Domains always run in parallel; output order is fixed (ARC, SRE, SEC, DAT).

## No-Gos

- No changes to existing domain skills or base prompts
- No auto-commit of review results
- No numeric scoring (status is pass/partial/fail/locked)
- No CI pipeline integration (deferred)
