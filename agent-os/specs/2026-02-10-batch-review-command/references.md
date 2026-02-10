# References: Batch Review Command (`/review-all`)

## Files Studied

### Domain SKILL.md Orchestrators (delegated to, not modified)
- `.claude/skills/review-arch/SKILL.md` — Architecture review orchestrator (4 zoom-level subagents)
- `.claude/skills/review-sre/SKILL.md` — SRE review orchestrator (ROAD subagents)
- `.claude/skills/review-security/SKILL.md` — Security review orchestrator (STRIDE subagents)
- `.claude/skills/review-data/SKILL.md` — Data review orchestrator (4 pillar subagents)

### Prior Spec (maturity model)
- `agent-os/specs/2026-02-09-summary-reports-maturity-scoring/` — Established the cascading maturity model (Hygiene → L1 → L2 → L3) that review-all aggregates across domains

### Product Context
- `agent-os/product/roadmap.md` — Defines batch review as Issue #16

## Design Decisions

- Batch orchestrator delegates to existing SKILL.md files via Task agents (general-purpose subagent type)
- Each Task agent has full tool access to spawn its own 4 sub-agents as defined in the domain SKILL.md
- Maturity status is extracted from sub-report tables, not re-computed
- Output directory `.code-review/<batch-name>/` follows a flat structure: summary files + domain sub-reports
- `summary.json` schema designed for future CI integration and trend analysis
