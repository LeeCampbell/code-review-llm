# References: Summary Reports with Maturity Scoring

## Files Studied

### Base Prompts (to be modified)
- `.claude/prompts/architecture/_base.md` — Architecture review base context with C4 zoom levels
- `.claude/prompts/sre/_base.md` — SRE review base context with SEEMS/FaCTOR
- `.claude/prompts/security/_base.md` — Security review base context with STRIDE/DREAD-lite
- `.claude/prompts/data/_base.md` — Data review base context with DAMA DMBOK/Data Mesh

### SKILL.md Orchestrators (to be modified)
- `.claude/skills/review-arch/SKILL.md` — Architecture review orchestrator (4 zoom-level subagents)
- `.claude/skills/review-sre/SKILL.md` — SRE review orchestrator (ROAD subagents)
- `.claude/skills/review-security/SKILL.md` — Security review orchestrator (STRIDE subagents)
- `.claude/skills/review-data/SKILL.md` — Data review orchestrator (4 pillar subagents)

### Product Context
- `agent-os/product/roadmap.md` — Defines the cascading maturity model (Hygiene → L1 → L2 → L3)

## Design Decisions

- Maturity criteria are domain-specific but follow the same 4-level structure across all domains
- Subagent prompts do NOT change — they inherit maturity tagging from `_base.md`
- The SKILL.md orchestrators handle maturity aggregation and the new output format
- The headline cross-domain summary table is deferred to Issue #16 (`/review-all`)
