# Slack MCP Server (Python)

A Python implementation of a Model Context Protocol (MCP) server for Slack integration. This server allows AI assistants to interact with Slack workspaces through a standardized interface.

## Prerequisites

- Python 3.12+
- A Slack Bot Token with appropriate permissions
- Slack Team ID

## Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt
```

### Using pip

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

- `SLACK_BOT_TOKEN`: Your Slack bot token (required)
- `SLACK_TEAM_ID`: Your Slack team/workspace ID (required)
- `SLACK_CHANNEL_IDS`: Comma-separated list of channel IDs to limit access (optional)

## Usage

### Running locally

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_TEAM_ID="T1234567890"
python slack_mcp_server.py
```

### Running with Docker

Build the image:

```bash
docker build -t slack-mcp-server .
```

Run the container:

```bash
docker run -e SLACK_BOT_TOKEN="xoxb-your-bot-token" \
           -e SLACK_TEAM_ID="T1234567890" \
           slack-mcp-server
```

## Slack Bot Setup

1. Create a new Slack app at https://api.slack.com/apps
2. Add the following OAuth scopes to your bot:
   - `channels:read`
   - `chat:write`
   - `groups:read`
   - `reactions:write`
   - `users:read`
   - `users.profile:read`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token

## MCP Integration

This server implements the Model Context Protocol and exposes the following tools:

- `slack_list_channels`: List available channels
- `slack_post_message`: Post a message to a channel
- `slack_reply_to_thread`: Reply to a message thread
- `slack_add_reaction`: Add an emoji reaction
- `slack_get_channel_history`: Get recent messages from a channel
- `slack_get_thread_replies`: Get all replies in a thread
- `slack_get_users`: List workspace users
- `slack_get_user_profile`: Get detailed user profile

## Development

### Project Structure

```
.
├── main.py  # Main server implementation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
└── README.md          # This file
```

### Adding New Tools

To add a new tool:

1. Define the tool schema in the `TOOLS` list
2. Add the corresponding method to `SlackClient`
3. Handle the tool call in the `call_tool` function

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.