"""Claude API client wrapper for code analysis."""

from __future__ import annotations

import json
from typing import Any, Dict

from anthropic import Anthropic

from config import Config, default_config


class ClaudeClient:
    """Wrapper for Claude API interactions."""

    def __init__(self, config: Config = default_config):
        """Initialize Claude client.

        Args:
            config: Configuration settings. Uses default if not provided.
        """
        config.validate()
        self.config = config
        self.client = Anthropic(api_key=config.anthropic_api_key)

    def analyze(self, prompt: str, code: str, language: str) -> Dict[str, Any]:
        """Analyze code using Claude.

        Args:
            prompt: The analysis prompt template.
            code: The code to analyze.
            language: Programming language of the code.

        Returns:
            Parsed JSON response from Claude.
        """
        # Use replace instead of format to avoid issues with JSON braces in prompt
        formatted_prompt = prompt.replace("{language}", language).replace("{code_content}", code)

        message = self.client.messages.create(
            model=self.config.claude_model,
            max_tokens=self.config.max_tokens,
            messages=[
                {"role": "user", "content": formatted_prompt}
            ]
        )

        response_text = message.content[0].text
        return self._parse_json_response(response_text)

    def analyze_with_context(
        self,
        prompt: str,
        code: str,
        language: str,
        git_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze code with git metrics context.

        Args:
            prompt: The analysis prompt template.
            code: The code to analyze.
            language: Programming language of the code.
            git_metrics: Git metrics for the file.

        Returns:
            Parsed JSON response from Claude.
        """
        # Use replace instead of format to avoid issues with JSON braces in prompt
        formatted_prompt = (prompt
            .replace("{language}", language)
            .replace("{code_content}", code)
            .replace("{git_metrics}", json.dumps(git_metrics, indent=2))
        )

        message = self.client.messages.create(
            model=self.config.claude_model,
            max_tokens=self.config.max_tokens,
            messages=[
                {"role": "user", "content": formatted_prompt}
            ]
        )

        response_text = message.content[0].text
        return self._parse_json_response(response_text)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from Claude's response.

        Args:
            response: Raw response text from Claude.

        Returns:
            Parsed JSON dictionary.
        """
        # Try to extract JSON from response
        # Claude may wrap JSON in markdown code blocks
        text = response.strip()

        # Remove markdown code block if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Return error structure if parsing fails
            return {
                "error": f"Failed to parse JSON response: {e}",
                "raw_response": response
            }
