"""Code health analysis orchestrator using Claude API."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_client import ClaudeClient
from config import Config, default_config


# Language detection by file extension
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".tf": "terraform",
    ".hcl": "hcl",
}


def detect_language(file_path: str) -> Optional[str]:
    """Detect programming language from file extension.

    Args:
        file_path: Path to the file.

    Returns:
        Language name or None if unsupported.
    """
    ext = Path(file_path).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext)


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory.

    Args:
        prompt_name: Name of the prompt file (without extension).

    Returns:
        Prompt template content.
    """
    # Find prompts directory relative to this file
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_path = prompts_dir / f"{prompt_name}.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    return prompt_path.read_text()


def analyze_file(
    file_path: str,
    config: Config = default_config,
    client: Optional[ClaudeClient] = None
) -> Dict[str, Any]:
    """Analyze a single file for code health.

    Args:
        file_path: Path to the file to analyze.
        config: Configuration settings.
        client: Optional pre-configured Claude client.

    Returns:
        Analysis results dictionary.
    """
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    language = detect_language(file_path)
    if not language:
        return {"error": f"Unsupported file type: {path.suffix}"}

    code = path.read_text()

    if not code.strip():
        return {"error": "File is empty"}

    prompt = load_prompt("code_health_score")

    if client is None:
        client = ClaudeClient(config)

    result = client.analyze(prompt, code, language)

    # Add metadata
    result["file_path"] = str(path.absolute())
    result["language"] = language
    result["lines_of_code"] = len(code.splitlines())

    return result


def analyze_files(
    file_paths: List[str],
    config: Config = default_config
) -> List[Dict[str, Any]]:
    """Analyze multiple files for code health.

    Args:
        file_paths: List of file paths to analyze.
        config: Configuration settings.

    Returns:
        List of analysis results.
    """
    client = ClaudeClient(config)
    results = []

    for file_path in file_paths:
        print(f"Analyzing: {file_path}", file=sys.stderr)
        result = analyze_file(file_path, config, client)
        results.append(result)

    return results


def main():
    """CLI entry point for code health analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze code health using Claude API"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Files to analyze"
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
        if len(args.files) == 1:
            results = analyze_file(args.files[0])
        else:
            results = analyze_files(args.files)

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
