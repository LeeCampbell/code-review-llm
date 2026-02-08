# Tech Stack

## Review Engine (Cloud)

- **Claude Code CLI** - Primary review orchestrator
- **Claude Code Skills** - Review commands (`/review-arch`, `/review-sre`, etc.)
- **Claude Code Agents** - Specialized subagents per review pillar
- **Markdown Prompts** - LLM-agnostic review checklists in `.claude/prompts/`

## Review Engine (Local)

- **Ollama** - Local LLM inference server
- **Docker** - Containerized Ollama with pre-loaded models (DeepSeek R1)
- **Python** - Ollama API client prototype (`python/code_review.py`)

## Infrastructure

- **Git/GitHub** - Version control and collaboration
- **Docker Compose** - GPU-accelerated local inference setup
