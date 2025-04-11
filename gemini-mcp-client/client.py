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
    server_configs = json.load(config_file)

# Extract the configuration for the "fileops" server
all_server_params = {}
for config in server_configs['mcp_configs']:
    name = config.get("name")
    command = config.get("command")
    args = config.get("args")
    env = config.get("env")
    if name and command and args and env:
        all_server_params[name] = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

active_mcp_server_param = all_server_params["jetbrains"]

class GeminiMCPClient:
    def __init__(self):
        """Initialize session and client objects."""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def connect_to_server(self):
        """Connect to the server using the provided script path."""
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(active_mcp_server_param))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        response = await self.session.list_tools()
        self.tools = response.tools
        # Print text in light grey (\033[90m ... \033[0m)
        print("\033[90m\nConnected to server with tools:", [tool.name for tool in self.tools], "\033[0m")

    async def process_query(self, chat: genai.chats.Chat, query: str):
        """Process a user query and handle tool calls."""
        
        system_instructions = "You are a software engineering agent for Android working on android studio. There is a project open and you are working on it. You can use the tools available to you to help with your tasks. You can also call functions to get information about the project and its files."

        tools = types.Tool(function_declarations=[
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in self.tools
        ])

        response = chat.send_message(
            message=query,
            config=types.GenerateContentConfig(
                system_instruction=system_instructions,
                tools=[tools]
                )
            
        )

        # Process response and handle tool calls
        while response.function_calls:
            function_response_parts = []
            for function_call in response.function_calls:
                tool_name = function_call.name
                tool_args = function_call.args
                # Tool prints in green for better formatting.
                print(f"\033[92m[Calling tool {tool_name} with args {tool_args}]\033[0m")
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
                config=types.GenerateContentConfig(   
                    system_instruction=system_instructions, 
                    tools=[tools]
                )
            )

        return response.text

    async def chat_loop(self):
        """Run an interactive chat loop."""
        # Chat startup messages in light grey.
        print("\033[90m\nMCP Client Started!\033[0m")
        print("\033[90mType your queries or 'quit' to exit.\033[0m")

        chat = self.gemini.chats.create(
            model='gemini-2.5-pro-preview-03-25',
            )
        
        while True:
            try:
                # User message prompt in blue.
                query = input("\n\033[94mUser:\033[0m ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(chat, query)
                # Gemini messages in purple.
                print("\n\033[95mGemini:\033[0m " + response)

            except Exception as e:
                # Error messages in light grey.
                print(f"\033[90m\nError: {str(e)}\033[0m")

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
