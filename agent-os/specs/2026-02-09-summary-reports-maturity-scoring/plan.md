# Plan: Summary Reports with Maturity Scoring

## Issue

#13 — Add cascading maturity model (Hygiene → L1 → L2 → L3) to each review domain's sub-report.

## Scope

8 files modified, 0 new commands, 0 new subagents.

## Tasks

### Task 1: Save Spec Documentation
Create this spec folder with plan, shape, and references.

### Task 2–5: Update `_base.md` for Each Domain
Add `## Maturity Model` section to each domain's base prompt with:
- Domain-specific criteria table (Hygiene → L3)
- Tagging rules (HYG/L1/L2/L3)
- Criteria assessment instructions (Met/Not met/Partially met)
- Updated output table with Maturity column

| Task | Domain | File |
|------|--------|------|
| 2 | Architecture | `.claude/prompts/architecture/_base.md` |
| 3 | SRE | `.claude/prompts/sre/_base.md` |
| 4 | Security | `.claude/prompts/security/_base.md` |
| 5 | Data | `.claude/prompts/data/_base.md` |

### Task 6–9: Update `SKILL.md` for Each Domain
Replace Step 3 (synthesis) and Output Format with maturity-aware structure:
- Maturity status table (pass/partial/fail/locked)
- Hygiene section (failures block all levels)
- Next achievable level (detailed criterion assessment)
- Higher level preview (brief)
- Detailed findings table with Maturity column

| Task | Domain | File |
|------|--------|------|
| 6 | Architecture | `.claude/skills/review-arch/SKILL.md` |
| 7 | SRE | `.claude/skills/review-sre/SKILL.md` |
| 8 | Security | `.claude/skills/review-security/SKILL.md` |
| 9 | Data | `.claude/skills/review-data/SKILL.md` |

### Task 10: Verify
Run `/review-sre` against sample code to verify new output format.
