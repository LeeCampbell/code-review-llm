#!/usr/bin/env python3
"""Main entry point for code quality analysis.

This script orchestrates the full analysis pipeline:
1. Extract git metrics from the repository
2. Identify hotspots (frequently changed files)
3. Analyze code health using Claude API
4. Generate prioritized report

Usage:
    python analyze.py /path/to/repo
    python analyze.py /path/to/repo --max-files 20 --output ./my-results
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from config import Config, default_config
from git_metrics import extract_metrics, get_hotspots
from hotspot_analyzer import analyze_repository
from report_generator import save_results


def run_git_metrics_only(repo_path: str, output_dir: Optional[Path] = None) -> None:
    """Run only git metrics extraction (no Claude API calls).

    Args:
        repo_path: Path to the git repository.
        output_dir: Optional output directory.
    """
    print(f"Extracting git metrics from: {repo_path}")
    metrics = extract_metrics(repo_path)

    hotspots = get_hotspots(metrics)
    print(f"\nFound {len(metrics)} files, {len(hotspots)} hotspots")

    if hotspots:
        print("\nTop Hotspots:")
        print("-" * 60)
        for m in hotspots[:10]:
            print(
                f"  {m.file_path}: "
                f"{m.change_frequency} commits, "
                f"{m.recent_changes} recent, "
                f"{m.unique_authors} authors"
            )

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "git_metrics.json"
        output_file.write_text(
            json.dumps([m.to_dict() for m in metrics], indent=2)
        )
        print(f"\nMetrics saved to: {output_file}")


def run_full_analysis(
    repo_path: str,
    max_files: int = 10,
    output_dir: Optional[Path] = None
) -> None:
    """Run full analysis with Claude API.

    Args:
        repo_path: Path to the git repository.
        max_files: Maximum number of files to analyze.
        output_dir: Optional output directory.
    """
    repo_name = Path(repo_path).name

    print(f"Running full analysis on: {repo_path}")
    print(f"Max files to analyze: {max_files}")
    print()

    analyses = analyze_repository(repo_path, max_files)

    if not analyses:
        print("No hotspots to analyze.")
        return

    # Convert to dictionaries
    results = [a.to_dict() for a in analyses]

    # Save results
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        from report_generator import generate_markdown_report
        (output_dir / "hotspots.json").write_text(
            json.dumps(results, indent=2)
        )
        generate_markdown_report(results, repo_name, output_dir)
        print(f"\nResults saved to: {output_dir}")
    else:
        results_dir = save_results(results, repo_name)
        print(f"\nResults saved to: {results_dir}")

    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)

    priority_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        priority = r.get("priority_analysis", {}).get("priority", "LOW")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    for priority, count in priority_counts.items():
        if count > 0:
            print(f"  {priority}: {count} files")

    print()
    print("Top Issues:")
    for r in results[:5]:
        file_path = r.get("file_path", "Unknown")
        health = r.get("health_analysis", {}).get("health_score", "N/A")
        priority = r.get("priority_analysis", {}).get("priority", "N/A")
        print(f"  [{priority}] {file_path} (health: {health}/10)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Code quality analysis using Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract git metrics only (no API calls)
  python analyze.py /path/to/repo --metrics-only

  # Full analysis with Claude API
  python analyze.py /path/to/repo

  # Analyze top 20 hotspots
  python analyze.py /path/to/repo --max-files 20

  # Save to specific directory
  python analyze.py /path/to/repo --output ./my-analysis
        """
    )

    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    parser.add_argument(
        "--metrics-only",
        action="store_true",
        help="Only extract git metrics (no Claude API calls)"
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
        type=Path,
        help="Output directory (default: results/{repo}-{timestamp})"
    )

    args = parser.parse_args()

    try:
        if args.metrics_only:
            run_git_metrics_only(args.repo_path, args.output)
        else:
            run_full_analysis(args.repo_path, args.max_files, args.output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAnalysis interrupted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
