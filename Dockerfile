# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the application
COPY slack_mcp_server.py .

# Set environment variables (these should be overridden at runtime)
ENV SLACK_BOT_TOKEN=""
ENV SLACK_TEAM_ID=""
ENV SLACK_CHANNEL_IDS=""

# Run the server
ENTRYPOINT ["python", "main.py"]