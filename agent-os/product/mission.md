# Product Mission

## Problem

Code reviews lack depth and breadth. Most reviews focus on either the big picture or the details, rarely both. They tend to evaluate through a single lens (security, reliability, scalability) rather than multiple perspectives simultaneously. Reviews often fail to provide clear, actionable guidance on how to move forward.

## Target Users

- **CTOs and Tech Leaders** - Assess codebase maturity and technical debt across teams
- **Engineering Teams** - Get structured, expert-level code reviews as part of day-to-day workflow

## Solution

A multi-perspective code review system that runs specialized subagents in parallel, each backed by industry frameworks:

- **Multi-perspective parallel reviews** - 4 subagents per domain, each with framework-backed checklists (STRIDE, ROAD, C4, DAMA DMBOK)
- **Portable prompt library** - LLM-agnostic prompts that work with Claude Code in the cloud or locally via Ollama with open-source models
- **Actionable, structured output** - Severity-ranked findings with specific file locations and recommendations
- **Summary reviews** - Provide next-best-actions for immediate priorities
- **Detailed reviews** - Document all future work comprehensively
- **Hygiene factors and maturity levels** - Reports highlight critical issues to address and aspirational targets to motivate teams
