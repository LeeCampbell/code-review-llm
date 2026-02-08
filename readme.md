# Code Review LLM

A sophisticated, multi-perspective code review system that helps CTOs and technology leaders understand the maturity of their codebase. Run reviews with Claude Code in the cloud, or locally in Docker using Ollama with smaller open-source LLMs.

## Review Domains

Each domain runs 4 specialized subagents in parallel, producing a consolidated report with prioritized findings.

| Domain | Command | Framework | What It Evaluates |
|--------|---------|-----------|-------------------|
| **Architecture** | `/review-arch` | C4 zoom levels (Code, Service, System, Landscape) | SOLID, DDD, Clean Architecture, Release It! stability patterns, EIP, ADR compliance |
| **SRE** | `/review-sre` | ROAD (Response, Observability, Availability, Delivery) | SEEMS/FaCTOR failure analysis, SLOs, circuit breakers, deployment safety |
| **Security** | `/review-security` | STRIDE threat modeling | Authentication, data protection, input validation, audit trails, DoS resilience |
| **Data** | `/review-data` | DAMA DMBOK + Data Mesh | Schema design, data contracts, quality SLOs, PII governance, lineage |

### Coming Soon

| Domain | Focus |
|--------|-------|
| **Product** | Feature completeness, user journey, accessibility |
| **UX** | Usability heuristics, consistency, responsiveness |

## How It Works

```
/review-arch src/                    # Review architecture of src/
/review-sre src/api/                 # SRE review of the API layer
/review-security .                   # Security review of entire project
/review-data src/pipelines/          # Data review of pipeline code
```

Each review command:

1. Spawns 4 specialized subagents in parallel (one per pillar)
2. Each agent reads shared prompt templates from `.claude/prompts/`
3. Agents independently analyze the code against their checklist
4. Results are deduplicated, prioritized by severity, and consolidated into a single report

### Output

Reports include:

- Executive summary with finding counts by severity (HIGH / MEDIUM / LOW)
- Detailed findings per pillar with file locations and recommendations
- Consolidated action items table sorted by priority
- Positive patterns observed

## Running Reviews

### With Claude Code (Cloud)

Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and run from the target project directory:

```bash
# Copy the .claude/ directory into your project
cp -r .claude/ /path/to/your/project/.claude/

# Run a review
claude "/review-arch src/"
```

### With Docker + Ollama (Local)

For air-gapped or cost-sensitive environments, run reviews locally using Ollama with open-source models. The shared prompt templates in `.claude/prompts/` are designed to work with any LLM.

#### Quick Start

Build and run the Ollama container with DeepSeek R1:

```bash
# Build (pulls ~5GB: 1.5GB Ollama image + model weights)
docker build -f .devcontainer/deepseek-r1.014b.dockerfile -t ollama-deepseek:1.0 .

# Run
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama-deepseek ollama-deepseek:1.0

# Verify
curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-r1:14b",
  "messages": [{ "role": "user", "content": "What LLM are you?" }],
  "stream": false
}'
```

#### Available Models

| Dockerfile | Model | Size | Use Case |
|-----------|-------|------|----------|
| `deepseek-r1.001.5b` | DeepSeek R1 1.5B | ~1.5GB | Quick smoke tests |
| `deepseek-r1.014b` | DeepSeek R1 14B | ~9GB | Good balance of quality and speed |
| `deepseek-r1.032b` | DeepSeek R1 32B | ~20GB | Higher quality reviews |
| `deepseek-r1.070b` | DeepSeek R1 70B | ~40GB | Best local quality |
| `deepseek-r1.671b` | DeepSeek R1 671B | ~400GB | Full model (requires significant hardware) |

#### Docker Compose (GPU)

For GPU-accelerated inference:

```bash
cd .devcontainer
docker compose up -d
```

#### Cleanup

```bash
docker container stop ollama-deepseek
docker container rm ollama-deepseek    # Remove to reclaim disk
```

## Project Structure

```
.claude/
├── prompts/                    # Shared review checklists (LLM-agnostic)
│   ├── architecture/
│   │   ├── _base.md            # C4 zoom levels, glossary, severity definitions
│   │   ├── code.md             # SOLID, DDD tactical, testability, naming
│   │   ├── service.md          # Bounded contexts, layering, deployability
│   │   ├── system.md           # Stability patterns, API contracts, coupling
│   │   └── landscape.md        # EIP, context maps, ADRs, tech-spec traceability
│   ├── sre/
│   │   ├── _base.md            # SEEMS/FaCTOR framework, terminology
│   │   ├── response.md         # Incident handling, runbook readiness
│   │   ├── observability.md    # Logging, metrics, tracing, SLIs
│   │   ├── availability.md     # SLOs, circuit breakers, resilience
│   │   └── delivery.md         # Deployment safety, rollback, feature flags
│   ├── security/
│   │   ├── _base.md            # STRIDE categories, DREAD-lite scoring
│   │   ├── authn-authz.md      # Authentication, authorization, sessions
│   │   ├── data-protection.md  # Encryption, secrets, data integrity
│   │   ├── input-validation.md # SQL injection, XSS, command injection
│   │   └── audit-resilience.md # Audit trails, rate limiting, DoS
│   └── data/
│       ├── _base.md            # Data quality dimensions, terminology
│       ├── architecture.md     # Schema design, interoperability, contracts
│       ├── engineering.md      # Logic verification, performance, error handling
│       ├── quality.md          # Freshness SLOs, accuracy, observability
│       └── governance.md       # PII classification, retention, lineage
├── agents/                     # Subagent definitions (Claude Code)
│   ├── arch-{code,service,system,landscape}.md
│   ├── sre-{response,observability,availability,delivery}.md
│   ├── security-{authn-authz,data-protection,input-validation,audit-resilience}.md
│   └── data-{architecture,engineering,quality,governance}.md
└── skills/                     # Review orchestrators (Claude Code)
    ├── review-arch/SKILL.md
    ├── review-sre/SKILL.md
    ├── review-security/SKILL.md
    └── review-data/SKILL.md

.devcontainer/                  # Docker + Ollama local setup
├── docker-compose.yml
└── deepseek-r1.*.dockerfile

python/
└── code_review.py              # Ollama API client (prototype)
```

## Frameworks and Sources

| Domain | Primary Sources |
|--------|----------------|
| Architecture | Domain-Driven Design (Evans), Modern Software Engineering (Farley), Release It! (Nygard), Enterprise Integration Patterns (Hohpe & Woolf), C4 Model (Brown) |
| SRE | SEEMS/FaCTOR failure analysis, ROAD framework, Google SRE Book |
| Security | STRIDE (Microsoft), DREAD-lite risk scoring, OWASP Top 10 |
| Data | DAMA DMBOK, Data Mesh (Dehghani), Data Governance for Everyone |
