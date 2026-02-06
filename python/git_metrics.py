"""Git metrics extraction for hotspot detection."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

from config import Config, default_config


@dataclass
class FileMetrics:
    """Git metrics for a single file."""

    file_path: str
    change_frequency: int = 0  # Total commits touching this file
    recent_changes: int = 0  # Changes in last N days
    unique_authors: int = 0  # Number of distinct contributors
    code_churn: int = 0  # Lines added + deleted
    lines_added: int = 0
    lines_deleted: int = 0
    coupling: List[str] = field(default_factory=list)  # Files changed together
    last_modified: str = ""
    age_days: int = 0
    authors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def run_git_command(args: List[str], repo_path: str) -> str:
    """Run a git command and return output.

    Args:
        args: Git command arguments.
        repo_path: Path to the git repository.

    Returns:
        Command output as string.
    """
    result = subprocess.run(
        ["git"] + args,
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {result.stderr}")
    return result.stdout


def get_file_list(repo_path: str, config: Config = default_config) -> List[str]:
    """Get list of tracked files in repository.

    Args:
        repo_path: Path to the git repository.
        config: Configuration settings.

    Returns:
        List of file paths relative to repo root.
    """
    output = run_git_command(["ls-files"], repo_path)
    files = [f.strip() for f in output.splitlines() if f.strip()]

    # Filter by supported extensions
    supported_exts = {".py", ".sql", ".js", ".ts", ".tsx", ".jsx", ".tf", ".hcl"}
    files = [f for f in files if Path(f).suffix.lower() in supported_exts]

    # Exclude patterns
    for pattern in config.exclude_patterns:
        files = [f for f in files if pattern.replace("*", "") not in f]

    return files


def get_commit_count(file_path: str, repo_path: str) -> int:
    """Get total number of commits for a file.

    Args:
        file_path: Path to file relative to repo root.
        repo_path: Path to the git repository.

    Returns:
        Number of commits.
    """
    output = run_git_command(
        ["rev-list", "--count", "HEAD", "--", file_path],
        repo_path
    )
    return int(output.strip()) if output.strip() else 0


def get_recent_commit_count(
    file_path: str,
    repo_path: str,
    days: int = 90
) -> int:
    """Get number of commits in recent period.

    Args:
        file_path: Path to file relative to repo root.
        repo_path: Path to the git repository.
        days: Number of days to look back.

    Returns:
        Number of recent commits.
    """
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    output = run_git_command(
        ["rev-list", "--count", f"--since={since_date}", "HEAD", "--", file_path],
        repo_path
    )
    return int(output.strip()) if output.strip() else 0


def get_authors(file_path: str, repo_path: str) -> List[str]:
    """Get list of unique authors for a file.

    Args:
        file_path: Path to file relative to repo root.
        repo_path: Path to the git repository.

    Returns:
        List of author names.
    """
    output = run_git_command(
        ["log", "--format=%an", "--", file_path],
        repo_path
    )
    authors = list(set(a.strip() for a in output.splitlines() if a.strip()))
    return authors


def get_code_churn(file_path: str, repo_path: str) -> Tuple[int, int]:
    """Get total lines added and deleted for a file.

    Args:
        file_path: Path to file relative to repo root.
        repo_path: Path to the git repository.

    Returns:
        Tuple of (lines_added, lines_deleted).
    """
    output = run_git_command(
        ["log", "--numstat", "--format=", "--", file_path],
        repo_path
    )

    added = 0
    deleted = 0

    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                added += int(parts[0]) if parts[0] != "-" else 0
                deleted += int(parts[1]) if parts[1] != "-" else 0
            except ValueError:
                continue

    return added, deleted


def get_last_modified(file_path: str, repo_path: str) -> Tuple[str, int]:
    """Get last modification date and age in days.

    Args:
        file_path: Path to file relative to repo root.
        repo_path: Path to the git repository.

    Returns:
        Tuple of (date string, age in days).
    """
    output = run_git_command(
        ["log", "-1", "--format=%aI", "--", file_path],
        repo_path
    )

    if not output.strip():
        return "", 0

    date_str = output.strip()
    # Parse ISO format date
    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    age_days = (datetime.now(date.tzinfo) - date).days

    return date_str[:10], age_days


def get_coupling(repo_path: str, limit: int = 100) -> Dict[str, List[str]]:
    """Analyze files that are frequently changed together.

    Args:
        repo_path: Path to the git repository.
        limit: Maximum number of commits to analyze.

    Returns:
        Dictionary mapping file to list of coupled files.
    """
    # Get recent commits
    output = run_git_command(
        ["log", f"-{limit}", "--format=%H"],
        repo_path
    )
    commits = [c.strip() for c in output.splitlines() if c.strip()]

    # Count co-occurrences
    co_occurrence: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for commit_hash in commits:
        # Get files changed in this commit
        files_output = run_git_command(
            ["show", "--name-only", "--format=", commit_hash],
            repo_path
        )
        files = [f.strip() for f in files_output.splitlines() if f.strip()]

        # Record co-occurrences
        for i, file1 in enumerate(files):
            for file2 in files[i + 1:]:
                co_occurrence[file1][file2] += 1
                co_occurrence[file2][file1] += 1

    # Convert to list of top coupled files (threshold: changed together 3+ times)
    coupling = {}
    for file_path, partners in co_occurrence.items():
        coupled = [p for p, count in partners.items() if count >= 3]
        if coupled:
            coupling[file_path] = sorted(coupled, key=lambda x: partners[x], reverse=True)[:5]

    return coupling


def extract_metrics(
    repo_path: str,
    config: Config = default_config
) -> List[FileMetrics]:
    """Extract git metrics for all files in a repository.

    Args:
        repo_path: Path to the git repository.
        config: Configuration settings.

    Returns:
        List of FileMetrics for each file.
    """
    repo = Path(repo_path).absolute()
    if not (repo / ".git").exists():
        raise ValueError(f"Not a git repository: {repo_path}")

    files = get_file_list(str(repo), config)
    coupling = get_coupling(str(repo))

    metrics = []
    for file_path in files:
        print(f"Extracting metrics: {file_path}", file=sys.stderr)

        try:
            authors = get_authors(file_path, str(repo))
            lines_added, lines_deleted = get_code_churn(file_path, str(repo))
            last_modified, age_days = get_last_modified(file_path, str(repo))

            file_metrics = FileMetrics(
                file_path=file_path,
                change_frequency=get_commit_count(file_path, str(repo)),
                recent_changes=get_recent_commit_count(file_path, str(repo), config.recent_days),
                unique_authors=len(authors),
                authors=authors,
                code_churn=lines_added + lines_deleted,
                lines_added=lines_added,
                lines_deleted=lines_deleted,
                coupling=coupling.get(file_path, []),
                last_modified=last_modified,
                age_days=age_days
            )
            metrics.append(file_metrics)

        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            continue

    return metrics


def get_hotspots(
    metrics: List[FileMetrics],
    config: Config = default_config
) -> List[FileMetrics]:
    """Filter and sort files by hotspot score.

    Args:
        metrics: List of file metrics.
        config: Configuration settings.

    Returns:
        Sorted list of hotspots (highest activity first).
    """
    # Filter by minimum change threshold
    hotspots = [m for m in metrics if m.change_frequency >= config.hotspot_threshold]

    # Sort by combined score (recent changes weighted higher)
    hotspots.sort(
        key=lambda m: (m.recent_changes * 2 + m.change_frequency),
        reverse=True
    )

    return hotspots


def main():
    """CLI entry point for git metrics extraction."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract git metrics for code analysis"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--hotspots-only",
        action="store_true",
        help="Only output files meeting hotspot threshold"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )

    args = parser.parse_args()

    try:
        metrics = extract_metrics(args.repo_path)

        if args.hotspots_only:
            metrics = get_hotspots(metrics)

        results = [m.to_dict() for m in metrics]

        indent = 2 if args.pretty else None
        output = json.dumps(results, indent=indent)

        if args.output:
            Path(args.output).write_text(output)
            print(f"Results written to: {args.output}", file=sys.stderr)
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
