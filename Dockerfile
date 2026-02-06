# Code Review LLM - Claude-based code quality analysis
FROM python:3.11-slim

LABEL maintainer="Lee Campbell"
LABEL description="CodeScene-like code quality analysis using Claude API"

# Install git (required for git metrics extraction)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up the tool directory
WORKDIR /opt/code-review

# Copy requirements and install dependencies
COPY .devcontainer/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the tool code
COPY python/ ./python/
COPY prompts/ ./prompts/

# Copy entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create results directory
RUN mkdir -p /opt/code-review/results

# Set PYTHONPATH so modules can be found
ENV PYTHONPATH=/opt/code-review/python

# Default working directory for mounted repos
WORKDIR /repo

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["--help"]
