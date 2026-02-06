#!/bin/bash
set -e

TOOL_DIR="/opt/code-review/python"

show_help() {
    cat << EOF
Code Review LLM - Claude-based code quality analysis

Usage:
  docker run -it --rm -v "\$(pwd):/repo" -e ANTHROPIC_API_KEY=\$KEY code-review:latest <command> [options]

Commands:
  inspect [options]     Run full code health + hotspot analysis
  metrics [options]     Extract git metrics only (no API calls)
  health <file>         Analyze a single file's code health
  help                  Show this help message

Options for 'inspect' and 'metrics':
  --max-files, -n NUM   Maximum files to analyze (default: 10)
  --output, -o DIR      Output directory (default: ./code-review-results)
  --pretty              Pretty print JSON output

Environment Variables:
  ANTHROPIC_API_KEY     Required for 'inspect' and 'health' commands

Examples:
  # Full analysis of current directory
  docker run -it --rm -v "\$(pwd):/repo" -e ANTHROPIC_API_KEY=\$KEY code-review:latest inspect

  # Git metrics only (no API key needed)
  docker run -it --rm -v "\$(pwd):/repo" code-review:latest metrics

  # Analyze specific file
  docker run -it --rm -v "\$(pwd):/repo" -e ANTHROPIC_API_KEY=\$KEY code-review:latest health src/main.py

  # Analyze top 20 hotspots
  docker run -it --rm -v "\$(pwd):/repo" -e ANTHROPIC_API_KEY=\$KEY code-review:latest inspect -n 20

EOF
}

case "$1" in
    inspect)
        shift
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "Error: ANTHROPIC_API_KEY environment variable is required for 'inspect'"
            echo "Usage: docker run -e ANTHROPIC_API_KEY=your-key ..."
            exit 1
        fi
        python "$TOOL_DIR/analyze.py" /repo "$@"
        ;;

    metrics)
        shift
        python "$TOOL_DIR/analyze.py" /repo --metrics-only "$@"
        ;;

    health)
        shift
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "Error: ANTHROPIC_API_KEY environment variable is required for 'health'"
            exit 1
        fi
        if [ -z "$1" ]; then
            echo "Error: Please specify a file to analyze"
            echo "Usage: docker run ... code-review:latest health <file>"
            exit 1
        fi
        python "$TOOL_DIR/code_health.py" "/repo/$1" --pretty
        ;;

    help|--help|-h|"")
        show_help
        ;;

    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
