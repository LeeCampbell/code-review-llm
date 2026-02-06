"""Report generator for code quality analysis results."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from config import Config, default_config


def generate_markdown_report(
    analyses: List[Dict[str, Any]],
    repo_name: str,
    output_dir: Path
) -> str:
    """Generate a Markdown report from hotspot analyses.

    Args:
        analyses: List of hotspot analysis dictionaries.
        repo_name: Name of the repository.
        output_dir: Directory to write the report.

    Returns:
        Path to the generated report.
    """
    lines = [
        f"# Code Quality Report: {repo_name}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"**Total files analyzed:** {len(analyses)}",
        "",
    ]

    # Priority breakdown
    priority_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for analysis in analyses:
        priority = analysis.get("priority_analysis", {}).get("priority", "LOW")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    lines.extend([
        "### Priority Breakdown",
        "",
        "| Priority | Count |",
        "|----------|-------|",
    ])

    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = priority_counts.get(priority, 0)
        if count > 0:
            lines.append(f"| {priority} | {count} |")

    lines.extend(["", "---", ""])

    # Detailed findings
    lines.append("## Hotspot Details")
    lines.append("")

    for i, analysis in enumerate(analyses, 1):
        file_path = analysis.get("file_path", "Unknown")
        git_metrics = analysis.get("git_metrics", {})
        health = analysis.get("health_analysis", {})
        priority = analysis.get("priority_analysis", {})

        health_score = health.get("health_score", "N/A")
        priority_level = priority.get("priority", "N/A")
        summary = health.get("summary", "No summary available")

        lines.extend([
            f"### {i}. `{file_path}`",
            "",
            f"**Priority:** {priority_level} | **Health Score:** {health_score}/10",
            "",
            f"**Summary:** {summary}",
            "",
            "#### Git Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Commits | {git_metrics.get('change_frequency', 'N/A')} |",
            f"| Recent changes (90 days) | {git_metrics.get('recent_changes', 'N/A')} |",
            f"| Unique authors | {git_metrics.get('unique_authors', 'N/A')} |",
            f"| Code churn | {git_metrics.get('code_churn', 'N/A')} lines |",
            f"| Last modified | {git_metrics.get('last_modified', 'N/A')} |",
            "",
        ])

        # Issues
        factors = health.get("factors", {})
        all_issues = []
        for category, issues in factors.items():
            if isinstance(issues, list):
                for issue in issues:
                    if isinstance(issue, dict):
                        all_issues.append({
                            "category": category,
                            "issue": issue.get("issue", ""),
                            "location": issue.get("location", ""),
                            "severity": issue.get("severity", ""),
                            "description": issue.get("description", "")
                        })

        if all_issues:
            lines.extend([
                "#### Issues Found",
                "",
                "| Category | Issue | Location | Severity |",
                "|----------|-------|----------|----------|",
            ])
            for issue in all_issues:
                lines.append(
                    f"| {issue['category']} | {issue['issue']} | "
                    f"{issue['location']} | {issue['severity']} |"
                )
            lines.append("")

        # Recommendations
        recommendations = health.get("recommendations", [])
        if recommendations:
            lines.extend([
                "#### Recommendations",
                "",
            ])
            for rec in recommendations:
                if isinstance(rec, dict):
                    action = rec.get("action", "")
                    impact = rec.get("impact", "")
                    priority_num = rec.get("priority", "")
                    lines.append(f"- **[P{priority_num}]** {action}")
                    if impact:
                        lines.append(f"  - *Impact:* {impact}")
                else:
                    lines.append(f"- {rec}")
            lines.append("")

        # Technical debt reasoning
        reasoning = priority.get("reasoning", {})
        if reasoning:
            lines.extend([
                "#### Technical Debt Analysis",
                "",
                f"- **Change frequency impact:** {reasoning.get('change_frequency_impact', 'N/A')}",
                f"- **Health score impact:** {reasoning.get('health_score_impact', 'N/A')}",
            ])
            risk_factors = reasoning.get("risk_factors", [])
            if risk_factors:
                lines.append(f"- **Risk factors:** {', '.join(risk_factors)}")
            lines.append("")

        lines.extend(["---", ""])

    # Action plan
    lines.extend([
        "## Recommended Action Plan",
        "",
    ])

    critical = [a for a in analyses
                if a.get("priority_analysis", {}).get("priority") == "CRITICAL"]
    high = [a for a in analyses
            if a.get("priority_analysis", {}).get("priority") == "HIGH"]

    if critical:
        lines.extend([
            "### Immediate Actions (CRITICAL)",
            "",
        ])
        for a in critical:
            lines.append(f"1. Refactor `{a['file_path']}`")
        lines.append("")

    if high:
        lines.extend([
            "### Short-term Actions (HIGH)",
            "",
        ])
        for a in high:
            lines.append(f"1. Review and improve `{a['file_path']}`")
        lines.append("")

    # Footer
    lines.extend([
        "---",
        "",
        "*Report generated by code-review-llm using Claude API*",
    ])

    report_content = "\n".join(lines)
    report_path = output_dir / "report.md"
    report_path.write_text(report_content)

    return str(report_path)


def save_results(
    analyses: List[Dict[str, Any]],
    repo_name: str,
    config: Config = default_config
) -> Path:
    """Save analysis results to the results directory.

    Args:
        analyses: List of analysis dictionaries.
        repo_name: Name of the repository.
        config: Configuration settings.

    Returns:
        Path to the results directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir = Path(config.results_dir) / f"{repo_name}-{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save raw JSON data
    (results_dir / "hotspots.json").write_text(
        json.dumps(analyses, indent=2)
    )

    # Extract and save git metrics separately
    git_metrics = [a.get("git_metrics", {}) for a in analyses]
    (results_dir / "git_metrics.json").write_text(
        json.dumps(git_metrics, indent=2)
    )

    # Extract and save health scores separately
    health_scores = [
        {
            "file_path": a.get("file_path"),
            "health_score": a.get("health_analysis", {}).get("health_score"),
            "summary": a.get("health_analysis", {}).get("summary")
        }
        for a in analyses
    ]
    (results_dir / "health_scores.json").write_text(
        json.dumps(health_scores, indent=2)
    )

    # Generate markdown report
    generate_markdown_report(analyses, repo_name, results_dir)

    return results_dir


def main():
    """CLI entry point for report generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate reports from code quality analysis"
    )
    parser.add_argument(
        "input_file",
        help="Input JSON file with hotspot analyses"
    )
    parser.add_argument(
        "--repo-name",
        "-r",
        default="repository",
        help="Repository name for the report (default: repository)"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Output directory (default: results/{repo-name}-{timestamp})"
    )

    args = parser.parse_args()

    try:
        # Load analyses
        input_path = Path(args.input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {args.input_file}")

        analyses = json.loads(input_path.read_text())

        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            generate_markdown_report(analyses, args.repo_name, output_dir)
            print(f"Report generated in: {output_dir}")
        else:
            results_dir = save_results(analyses, args.repo_name)
            print(f"Results saved to: {results_dir}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
