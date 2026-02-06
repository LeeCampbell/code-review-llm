"""Configuration settings for code quality analysis."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file from project root (if it exists)
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# Also try loading from current working directory (for Docker usage)
_cwd_env = Path.cwd() / ".env"
if _cwd_env.exists():
    load_dotenv(_cwd_env)


@dataclass
class Config:
    """Configuration for code quality analysis."""

    # Claude API settings
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    claude_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096

    # Analysis settings
    supported_languages: tuple = (
        "python", "sql", "javascript", "typescript", "terraform", "hcl"
    )

    # Git metrics settings
    recent_days: int = 90  # Days to consider for "recent" changes
    hotspot_threshold: int = 5  # Minimum commits to be considered a hotspot

    # File filtering
    exclude_patterns: tuple = (
        "*.pyc", "__pycache__", ".git", "node_modules",
        "*.min.js", "*.min.css", "package-lock.json", "yarn.lock"
    )

    # Output settings
    results_dir: str = "results"

    def validate(self) -> None:
        """Validate configuration."""
        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Set it with: export ANTHROPIC_API_KEY='your-key'"
            )


# Default configuration instance
default_config = Config()
