#!/usr/bin/env python3
"""Slack MCP Server - A Model Context Protocol server for Slack integration."""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field, ValidationError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

# Tool argument type definitions using Pydantic
class ListChannelsArgs(BaseModel):
    limit: Optional[int] = Field(
        default=100,
        description="Maximum number of channels to return (default 100, max 200)"
    )
    cursor: Optional[str] = Field(
        default=None,
        description="Pagination cursor for next page of results"
    )

class PostMessageArgs(BaseModel):
    channel_id: str = Field(description="The ID of the channel to post to")
    text: str = Field(description="The message text to post")

class ReplyToThreadArgs(BaseModel):
    channel_id: str = Field(description="The ID of the channel containing the thread")
    thread_ts: str = Field(
        description="The timestamp of the parent message in the format '1234567890.123456'"
    )
    text: str = Field(description="The reply text")

class AddReactionArgs(BaseModel):
    channel_id: str = Field(description="The ID of the channel containing the message")
    timestamp: str = Field(description="The timestamp of the message to react to")
    reaction: str = Field(description="The name of the emoji reaction (without ::)")

class GetChannelHistoryArgs(BaseModel):
    channel_id: str = Field(description="The ID of the channel")
    limit: Optional[int] = Field(
        default=10,
        description="Number of messages to retrieve (default 10)"
    )

class GetThreadRepliesArgs(BaseModel):
    channel_id: str = Field(description="The ID of the channel containing the thread")
    thread_ts: str = Field(
        description="The timestamp of the parent message in the format '1234567890.123456'"
    )

class GetUsersArgs(BaseModel):
    cursor: Optional[str] = Field(
        default=None,
        description="Pagination cursor for next page of results"
    )
    limit: Optional[int] = Field(
        default=100,
        description="Maximum number of users to return (default 100, max 200)"
    )

class GetUserProfileArgs(BaseModel):
    user_id: str = Field(description="The ID of the user")


class SlackClient:
    """Client for interacting with Slack API."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient()
    
    async def get_channels(self, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get list of channels."""
        predefined_channel_ids = os.getenv("SLACK_CHANNEL_IDS")
        
        if not predefined_channel_ids:
            params = {
                "types": "public_channel",
                "exclude_archived": "true",
                "limit": str(min(limit, 200)),
                "team_id": os.getenv("SLACK_TEAM_ID")
            }
            
            if cursor:
                params["cursor"] = cursor
            
            response = await self.client.get(
                f"https://slack.com/api/conversations.list?{urlencode(params)}",
                headers=self.headers
            )
            return response.json()
        
        # Handle predefined channels
        channel_ids = [id.strip() for id in predefined_channel_ids.split(",")]
        channels = []
        
        for channel_id in channel_ids:
            params = {"channel": channel_id}
            response = await self.client.get(
                f"https://slack.com/api/conversations.info?{urlencode(params)}",
                headers=self.headers
            )
            data = response.json()
            
            if data.get("ok") and data.get("channel") and not data["channel"].get("is_archived"):
                channels.append(data["channel"])
        
        return {
            "ok": True,
            "channels": channels,
            "response_metadata": {"next_cursor": ""}
        }
    
    async def post_message(self, channel_id: str, text: str) -> Dict[str, Any]:
        """Post a message to a channel."""
        response = await self.client.post(
            "https://slack.com/api/chat.postMessage",
            headers=self.headers,
            json={
                "channel": channel_id,
                "text": text
            }
        )
        return response.json()
    
    async def post_reply(self, channel_id: str, thread_ts: str, text: str) -> Dict[str, Any]:
        """Reply to a thread."""
        response = await self.client.post(
            "https://slack.com/api/chat.postMessage",
            headers=self.headers,
            json={
                "channel": channel_id,
                "thread_ts": thread_ts,
                "text": text
            }
        )
        return response.json()
    
    async def add_reaction(self, channel_id: str, timestamp: str, reaction: str) -> Dict[str, Any]:
        """Add a reaction to a message."""
        response = await self.client.post(
            "https://slack.com/api/reactions.add",
            headers=self.headers,
            json={
                "channel": channel_id,
                "timestamp": timestamp,
                "name": reaction
            }
        )
        return response.json()
    
    async def get_channel_history(self, channel_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get channel message history."""
        params = {
            "channel": channel_id,
            "limit": str(limit)
        }
        
        response = await self.client.get(
            f"https://slack.com/api/conversations.history?{urlencode(params)}",
            headers=self.headers
        )
        return response.json()
    
    async def get_thread_replies(self, channel_id: str, thread_ts: str) -> Dict[str, Any]:
        """Get replies in a thread."""
        params = {
            "channel": channel_id,
            "ts": thread_ts
        }
        
        response = await self.client.get(
            f"https://slack.com/api/conversations.replies?{urlencode(params)}",
            headers=self.headers
        )
        return response.json()
    
    async def get_users(self, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get list of users."""
        params = {
            "limit": str(min(limit, 200)),
            "team_id": os.getenv("SLACK_TEAM_ID")
        }
        
        if cursor:
            params["cursor"] = cursor
        
        response = await self.client.get(
            f"https://slack.com/api/users.list?{urlencode(params)}",
            headers=self.headers
        )
        return response.json()
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        params = {
            "user": user_id,
            "include_labels": "true"
        }
        
        response = await self.client.get(
            f"https://slack.com/api/users.profile.get?{urlencode(params)}",
            headers=self.headers
        )
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Tool definitions - generated from Pydantic models
TOOLS = [
    Tool(
        name="slack_list_channels",
        description="List public or pre-defined channels in the workspace with pagination",
        inputSchema=ListChannelsArgs.model_json_schema()
    ),
    Tool(
        name="slack_post_message",
        description="Post a new message to a Slack channel",
        inputSchema=PostMessageArgs.model_json_schema()
    ),
    Tool(
        name="slack_reply_to_thread",
        description="Reply to a specific message thread in Slack",
        inputSchema=ReplyToThreadArgs.model_json_schema()
    ),
    Tool(
        name="slack_add_reaction",
        description="Add a reaction emoji to a message",
        inputSchema=AddReactionArgs.model_json_schema()
    ),
    Tool(
        name="slack_get_channel_history",
        description="Get recent messages from a channel",
        inputSchema=GetChannelHistoryArgs.model_json_schema()
    ),
    Tool(
        name="slack_get_thread_replies",
        description="Get all replies in a message thread",
        inputSchema=GetThreadRepliesArgs.model_json_schema()
    ),
    Tool(
        name="slack_get_users",
        description="Get a list of all users in the workspace with their basic profile information",
        inputSchema=GetUsersArgs.model_json_schema()
    ),
    Tool(
        name="slack_get_user_profile",
        description="Get detailed profile information for a specific user",
        inputSchema=GetUserProfileArgs.model_json_schema()
    )
]


async def main():
    """Main entry point for the Slack MCP server."""
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    team_id = os.getenv("SLACK_TEAM_ID")
    
    if not bot_token or not team_id:
        print("Please set SLACK_BOT_TOKEN and SLACK_TEAM_ID environment variables")
        exit(1)
    
    print("Starting Slack MCP Server...", flush=True)
    
    # Create server instance
    server = Server(
        name="Slack MCP Server",
        version="1.0.0"
    )
    
    # Initialize Slack client
    slack_client = SlackClient(bot_token)
    
    # Register tools
    for tool in TOOLS:
        server.add_tool(tool)
    
    @server.call_tool
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls."""
        print(f"Received tool call: {name} with args: {arguments}", flush=True)
        
        try:
            if name == "slack_list_channels":
                args = ListChannelsArgs(**arguments)
                response = await slack_client.get_channels(args.limit, args.cursor)
                
            elif name == "slack_post_message":
                args = PostMessageArgs(**arguments)
                response = await slack_client.post_message(args.channel_id, args.text)
                
            elif name == "slack_reply_to_thread":
                args = ReplyToThreadArgs(**arguments)
                response = await slack_client.post_reply(
                    args.channel_id,
                    args.thread_ts,
                    args.text
                )
                
            elif name == "slack_add_reaction":
                args = AddReactionArgs(**arguments)
                response = await slack_client.add_reaction(
                    args.channel_id,
                    args.timestamp,
                    args.reaction
                )
                
            elif name == "slack_get_channel_history":
                args = GetChannelHistoryArgs(**arguments)
                response = await slack_client.get_channel_history(
                    args.channel_id,
                    args.limit
                )
                
            elif name == "slack_get_thread_replies":
                args = GetThreadRepliesArgs(**arguments)
                response = await slack_client.get_thread_replies(
                    args.channel_id,
                    args.thread_ts
                )
                
            elif name == "slack_get_users":
                args = GetUsersArgs(**arguments)
                response = await slack_client.get_users(args.limit, args.cursor)
                
            elif name == "slack_get_user_profile":
                args = GetUserProfileArgs(**arguments)
                response = await slack_client.get_user_profile(args.user_id)
                
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except ValidationError as e:
            print(f"Validation error for tool {name}: {e}", flush=True)
            error_response = {"error": f"Invalid arguments: {e}"}
            return [TextContent(type="text", text=json.dumps(error_response))]
        except Exception as e:
            print(f"Error executing tool {name}: {e}", flush=True)
            error_response = {"error": str(e)}
            return [TextContent(type="text", text=json.dumps(error_response))]
    
    # Run the server
    async with stdio_server() as streams:
        print("Slack MCP Server running on stdio", flush=True)
        await server.run(
            streams.read_stream,
            streams.write_stream,
            server.create_initialization_options()
        )
    
    # Cleanup
    await slack_client.close()


def run():
    """Entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()