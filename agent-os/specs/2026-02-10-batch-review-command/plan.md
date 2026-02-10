# Plan: Batch Review Command (`/review-all`) — Issue #16

## Issue

#16 — Run all review domains at once, compare maturity across domains, and persist results to disk.

## Scope

1 new SKILL.md, 0 files modified, 4 Task agents orchestrated in parallel.

## Architecture Decision

**Delegate to existing skills** rather than directly spawning 16 agents. The `review-all` skill invokes 4 Task agents, each instructed to execute a domain review following its existing SKILL.md pattern. This avoids duplicating synthesis logic and ensures review-all automatically benefits from any future improvements to individual skills.

## Tasks

### Task 1: Save Spec Documentation
Create this spec folder with plan, shape, and references.

### Task 2: Create `review-all` SKILL.md
Create `.claude/skills/review-all/SKILL.md` with:
- Argument parsing (path, --name, --domains)
- Batch name resolution (tag → branch-hash → date-hash)
- Parallel domain review execution via Task agents
- Sub-report writing to `.code-review/<batch-name>/`
- Maturity extraction and summary generation (summary.md + summary.json)

### Task 3: Verify
- Run `/review-all .` to confirm end-to-end flow
- Check `.code-review/` directory is created with all expected files
- Verify `summary.json` is valid JSON with correct structure
- Verify `summary.md` contains maturity overview table with links
- Test `--domains ARC,SRE` to confirm domain filtering works

## Verification

- [ ] `/review-all <path>` runs all 4 domain reviews
- [ ] `--name` flag overrides batch name
- [ ] Batch name falls back correctly: tag → branch-hash → date-hash
- [ ] Output written to `.code-review/<batch-name>/`
- [ ] Each domain produces a `.md` sub-report
- [ ] `summary.md` contains headline maturity table with visual indicators
- [ ] `summary.json` contains machine-readable status per domain with run metadata
- [ ] `--domains` flag limits which domains run (case-insensitive)
- [ ] Domains not run are omitted from summary
- [ ] No files are auto-committed
