# Shape: Summary Reports with Maturity Scoring

## Problem

The 4 review domains (`/review-arch`, `/review-sre`, `/review-security`, `/review-data`) produce flat severity-ranked reports. There is no structured maturity assessment — findings aren't mapped to maturity levels, so teams can't see where they stand on a progression from baseline safety to excellence.

## Appetite

Small batch — changes are scoped to 8 existing files (4 `_base.md` + 4 `SKILL.md`). No new commands, no new subagents.

## Solution

Add a cascading maturity model (Hygiene → L1 → L2 → L3) to each domain. Each level requires the previous. The report structure changes from flat findings to maturity-aware output:

1. **Maturity status table** — shows pass/partial/fail/locked per level
2. **Hygiene section** — failures listed first (they block everything)
3. **Next achievable level** — detailed criterion-by-criterion assessment
4. **Higher level preview** — brief list of what comes next
5. **Detailed findings table** — now includes a Maturity column (HYG/L1/L2/L3)

## Rabbit Holes

- **Cross-domain summary table**: That's `/review-all` (Issue #16), not this issue. Each domain sub-report stands alone.
- **Subagent prompt changes**: Not needed — subagents inherit from `_base.md` and the maturity tagging instructions there are sufficient.
- **Weighted scoring**: No numeric scores. Status is pass/partial/fail/locked — simple and unambiguous.

## No-Gos

- No changes to subagent prompts (they inherit `_base.md`)
- No new CLI commands
- No cross-domain aggregation (future issue)
