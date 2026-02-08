# Product Roadmap

## Phase 1: MVP

- **4 review domains** with parallel subagents:
  - Architecture (`/review-arch`) - C4 zoom levels, DDD, Release It!, EIP
  - SRE (`/review-sre`) - ROAD framework, SEEMS/FaCTOR failure analysis
  - Security (`/review-security`) - STRIDE threat modeling
  - Data (`/review-data`) - DAMA DMBOK, Data Mesh principles
- **Summary reports** - Consolidated findings with severity-ranked action items
- **Maturity scoring** - Hygiene factors (must-fix) and aspirational maturity targets

## Phase 2: Post-Launch

- **Product review domain** - Feature completeness, user journey, accessibility
- **UX review domain** - Usability heuristics, consistency, responsiveness
- **Local Ollama support** - Docker-based reviews with open-source models for air-gapped environments
- **CI/CD integration** - Automated reviews triggered on releases (one per day), results published to the GitHub release
- **Tracking** - Each release review collects previous release reports as inputs to create a chart tracking maturity over time.
