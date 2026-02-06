"""Hotspot analyzer combining git metrics with code health analysis."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_client import ClaudeClient
from code_health import analyze_file, load_prompt
from config import Config, default_config
from git_metrics import FileMetrics, extract_metrics, get_hotspots


@dataclass
class HotspotAnalysis:
    """Combined analysis for a file hotspot."""

    file_path: str
    git_metrics: Dict[str, Any]
    health_analysis: Dict[str, Any]
    priority_analysis: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "git_metrics": self.git_metrics,
            "health_analysis": self.health_analysis,
            "priority_analysis": self.priority_analysis
        }


def analyze_hotspot(
    file_path: str,
    repo_path: str,
    git_metrics: FileMetrics,
    config: Config = default_config,
    client: Optional[ClaudeClient] = None
) -> HotspotAnalysis:
    """Perform full hotspot analysis on a file.

    Args:
        file_path: Path to the file relative to repo root.
        repo_path: Path to the git repository.
        git_metrics: Pre-extracted git metrics for the file.
        config: Configuration settings.
        client: Optional pre-configured Claude client.

    Returns:
        Complete hotspot analysis.
    """
    full_path = Path(repo_path) / file_path

    # Step 1: Get code health analysis
    health_analysis = analyze_file(str(full_path), config, client)

    if client is None:
        client = ClaudeClient(config)

    # Step 2: Get priority analysis combining git metrics + health
    priority_prompt = load_prompt("hotspot_priority")

    # Detect language from file extension
    ext_to_lang = {
        ".py": "python", ".sql": "sql", ".js": "javascript",
        ".ts": "typescript", ".tf": "terraform", ".hcl": "hcl"
    }
    language = ext_to_lang.get(full_path.suffix.lower(), "unknown")

    code = full_path.read_text() if full_path.exists() else ""

    # Use replace instead of format to avoid issues with JSON braces in prompt
    formatted_prompt = (priority_prompt
        .replace("{health_analysis}", json.dumps(health_analysis, indent=2))
        .replace("{git_metrics}", json.dumps(git_metrics.to_dict(), indent=2))
        .replace("{language}", language)
        .replace("{code_content}", code[:10000])  # Limit code size for context window
    )

    message = client.client.messages.create(
        model=config.claude_model,
        max_tokens=config.max_tokens,
        messages=[{"role": "user", "content": formatted_prompt}]
    )

    priority_analysis = client._parse_json_response(message.content[0].text)

    return HotspotAnalysis(
        file_path=file_path,
        git_metrics=git_metrics.to_dict(),
        health_analysis=health_analysis,
        priority_analysis=priority_analysis
    )


def analyze_repository(
    repo_path: str,
    max_files: int = 10,
    config: Config = default_config
) -> List[HotspotAnalysis]:
    """Analyze top hotspots in a repository.

    Args:
        repo_path: Path to the git repository.
        max_files: Maximum number of files to analyze.
        config: Configuration settings.

    Returns:
        List of hotspot analyses sorted by priority.
    """
    print(f"Extracting git metrics from: {repo_path}", file=sys.stderr)
    all_metrics = extract_metrics(repo_path, config)

    print(f"Found {len(all_metrics)} files, filtering hotspots...", file=sys.stderr)
    hotspots = get_hotspots(all_metrics, config)[:max_files]

    if not hotspots:
        print("No hotspots found meeting threshold criteria.", file=sys.stderr)
        return []

    print(f"Analyzing {len(hotspots)} hotspots...", file=sys.stderr)

    client = ClaudeClient(config)
    analyses = []

    for metrics in hotspots:
        print(f"  Analyzing: {metrics.file_path}", file=sys.stderr)
        try:
            analysis = analyze_hotspot(
                metrics.file_path,
                repo_path,
                metrics,
                config,
                client
            )
            analyses.append(analysis)
        except Exception as e:
            print(f"  Error analyzing {metrics.file_path}: {e}", file=sys.stderr)

    # Sort by priority score (if available)
    def get_priority_score(a: HotspotAnalysis) -> int:
        priority_map = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        priority = a.priority_analysis.get("priority", "LOW")
        return priority_map.get(priority, 0)

    analyses.sort(key=get_priority_score, reverse=True)

    return analyses


def main():
    """CLI entry point for hotspot analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze code hotspots combining git metrics and code health"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    parser.add_argument(
        "--max-files",
        "-n",
        type=int,
        default=10,
        help="Maximum number of hotspots to analyze (default: 10)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )

    args = parser.parse_args()

    try:
        analyses = analyze_repository(args.repo_path, args.max_files)

        results = [a.to_dict() for a in analyses]

        indent = 2 if args.pretty else None
        output = json.dumps(results, indent=indent)

        if args.output:
            Path(args.output).write_text(output)
            print(f"Results written to: {args.output}", file=sys.stderr)
        else:
            print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
