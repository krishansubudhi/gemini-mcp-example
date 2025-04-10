import asyncio
import os
import json
from typing import Optional
from contextlib import AsyncExitStack
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from google.genai import types

# Load environment variables from .env
load_dotenv()

# Load FILEOPS_SERVER_PARAMS from mcp-server-config.json
config_path = os.path.join(os.path.dirname(__file__), "mcp-server-config.json")
with open(config_path, "r") as config_file:
    server_config = json.load(config_file)

FILEOPS_SERVER_PARAMS = StdioServerParameters(
    command=server_config["command"],
    args=server_config["args"],
    env=server_config["env"]
)


class GeminiMCPClient:
    def __init__(self):
        """Initialize session and client objects."""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def connect_to_server(self):
        """Connect to the server using the provided script path."""
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(FILEOPS_SERVER_PARAMS))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        response = await self.session.list_tools()
        self.tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in self.tools])

    async def process_query(self, chat: genai.chats.Chat, query: str):
        """Process a user query and handle tool calls."""
        tools = types.Tool(function_declarations=[
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in self.tools
        ])

        response = chat.send_message(
            message=query,
            config=types.GenerateContentConfig(tools=[tools])
        )

        # Process response and handle tool calls
        while response.function_calls:
            function_response_parts = []
            for function_call in response.function_calls:
                tool_name = function_call.name
                tool_args = function_call.args
                print(f"[Calling tool {tool_name} with args {tool_args}]")
                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                    function_response = {'output': result}
                except Exception as e:
                    function_response = {'error': str(e)}

                function_response_part = types.Part.from_function_response(
                    name=tool_name,
                    response=function_response,
                )
                function_response_parts.append(function_response_part)

            response = chat.send_message(
                message=function_response_parts,
                config=types.GenerateContentConfig(tools=[tools])
            )

        return response.text

    async def chat_loop(self):
        """Run an interactive chat loop."""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        chat = self.gemini.chats.create(model='gemini-2.0-flash')

        while True:
            try:
                query = input("\nUser: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(chat, query)
                print("\nGemini: " + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    """Main function to run the MCP client."""
    client = GeminiMCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())