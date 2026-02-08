# Product Roadmap

## Phase 1: MVP

- **4 review domains** with parallel subagents:
  - Architecture (`/review-arch`) - C4 zoom levels, DDD, Release It!, EIP
  - SRE (`/review-sre`) - ROAD framework, SEEMS/FaCTOR failure analysis
  - Security (`/review-security`) - STRIDE threat modeling
  - Data (`/review-data`) - DAMA DMBOK, Data Mesh principles
- **Summary reports** - Headline summary table with per-level status indicators linking to detailed sub-reports
- **Maturity model** - Cascading levels where each level requires the previous:
  - **Hygiene** — Baseline safety (no SQL injection, no unbounded retries, no circular deps, no unmasked PII)
  - **Level 1 — Foundations** — Basics in place (module boundaries, health checks, auth/authz, schema docs, architecture diagrams published)
  - **Level 2 — Operational maturity** — Production-ready (ADRs, SLOs, circuit breakers, threat modelling, resilience modelling, data contracts)
  - **Level 3 — Excellence** — Best-in-class (fitness functions, chaos testing, automated security testing, data mesh patterns)
- **Report structure** per domain:
  - Hygiene failures listed first (block all levels)
  - Full detail on the next achievable level
  - Brief preview of higher levels
  - Detailed findings table with severity-ranked recommendations

## Phase 2: Post-Launch

- **Product review domain** - Feature completeness, user journey, accessibility
- **UX review domain** - Usability heuristics, consistency, responsiveness
- **Local Ollama support** - Docker-based reviews with open-source models for air-gapped environments
- **CI/CD integration** - Automated reviews triggered on releases (one per day), results published to the GitHub release
- **Tracking** - Each release review collects previous release reports as inputs to create a chart tracking maturity over time.
