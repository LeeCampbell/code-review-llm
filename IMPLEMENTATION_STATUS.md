# CodeScene-Like Analysis Implementation Status

## Overview

This implements a Claude-based code quality analysis system inspired by CodeScene, providing:
- Code health scoring (1-10 scale)
- Git metrics extraction (hotspots, churn, coupling)
- Technical debt prioritization
- Markdown + JSON reports

## Files Created

| File | Purpose | Status |
|------|---------|--------|
| `python/config.py` | Configuration settings | ✅ Complete |
| `python/claude_client.py` | Claude API wrapper | ✅ Complete |
| `python/code_health.py` | Code health analysis orchestrator | ✅ Complete |
| `python/git_metrics.py` | Git history extraction | ✅ Complete, tested |
| `python/hotspot_analyzer.py` | Combined git + health analysis | ✅ Complete |
| `python/report_generator.py` | Markdown/JSON report generation | ✅ Complete |
| `python/analyze.py` | Main CLI entry point | ✅ Complete |
| `prompts/code_health_score.md` | Health scoring prompt template | ✅ Complete |
| `prompts/hotspot_priority.md` | Prioritization prompt template | ✅ Complete |
| `.devcontainer/requirements.txt` | Added `anthropic` SDK | ✅ Updated |
| `Dockerfile` | Docker image for portable CLI | ✅ Complete, tested |
| `docker-entrypoint.sh` | Docker entrypoint script | ✅ Complete |
| `.env` | Environment variables (API key) | ✅ Created (gitignored) |

## Setup Required

1. **Environment Variable**: Set `ANTHROPIC_API_KEY` before running:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

2. **Install Dependencies** (done automatically in dev container):
   ```bash
   pip install -r .devcontainer/requirements.txt
   ```

## Usage

### Docker (Recommended)

Build the image once:
```bash
docker build -t code-review:latest .
```

Run from any repository:
```bash
# Show help
docker run --rm code-review:latest help

# Git metrics only (no API key needed)
docker run --rm -v "$(pwd):/repo" code-review:latest metrics

# Analyze a single file
docker run --rm -v "$(pwd):/repo" -e ANTHROPIC_API_KEY=$KEY code-review:latest health src/main.py

# Full analysis of repository
docker run --rm -v "$(pwd):/repo" -e ANTHROPIC_API_KEY=$KEY code-review:latest inspect

# Analyze top 20 hotspots
docker run --rm -v "$(pwd):/repo" -e ANTHROPIC_API_KEY=$KEY code-review:latest inspect -n 20
```

### Local Python

```bash
cd python

# Git metrics only
python analyze.py /path/to/repo --metrics-only

# Full analysis
python analyze.py /path/to/repo
python analyze.py /path/to/repo --max-files 20

# Individual components
python git_metrics.py /path/to/repo --pretty
python code_health.py /path/to/file.py --pretty
python report_generator.py hotspots.json --repo-name my-repo
```

## Verification Completed

- ✅ `git_metrics.py` tested - extracts metrics correctly
- ✅ All Python modules have valid syntax
- ✅ Prompt templates load correctly
- ✅ Claude API integration - working! Successfully analyzed code_review.py (health score: 3/10)

## Next Steps (in dev container)

1. Run `python analyze.py . --metrics-only` to verify git metrics
2. Set `ANTHROPIC_API_KEY` and run `python analyze.py .` for full analysis
3. Review generated report in `results/` directory

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  analyze.py (CLI entry point)                               │
│     ↓                                                       │
├─────────────────────────────────────────────────────────────┤
│  git_metrics.py          │  code_health.py                  │
│  - Extract commits       │  - Load prompts                  │
│  - Calculate churn       │  - Detect language               │
│  - Find coupling         │  - Call Claude API               │
├─────────────────────────────────────────────────────────────┤
│  hotspot_analyzer.py                                        │
│  - Combine git + health data                                │
│  - Calculate priority scores                                │
├─────────────────────────────────────────────────────────────┤
│  report_generator.py                                        │
│  - Generate Markdown report                                 │
│  - Save JSON artifacts                                      │
└─────────────────────────────────────────────────────────────┘
```
