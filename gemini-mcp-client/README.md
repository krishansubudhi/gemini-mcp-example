# Gemin MCP cli client
This is a commandline chat client which detects the fileops MCP server tools and creates a tool aware gemini client.

## Example

```
(gemini-mcp-client) krishansubudhi:~/gemini-mcp-example/gemini-mcp-client$ python client.py
```

[04/10/25 13:59:11] INFO     Processing request of type ListToolsRequest                                                                                                                                                 server.py:534

Connected to server with tools: ['ls', 'cat', 'grep', 'grepdir', 'mkdir', 'write']

MCP Client Started!
Type your queries or 'quit' to exit.

---

**User**: What does the code in /users/krishansubudhi/gemini-mcp-example/gemini-mcp-client/client.py do?

[Calling tool cat with args {'path': '/users/krishansubudhi/gemini-mcp-example/gemini-mcp-client/client.py'}]
[04/10/25 13:59:55] INFO     Processing request of type CallToolRequest                                                                                                                                                  server.py:534


**Gemini**: The code defines a `GeminiMCPClient` class that interacts with a server using the MCP (Maybe Container Protocol). It uses Google's Gemini API for chat functionality and interacts with a server that provides tools.


Here's a breakdown:

1.  **Imports:** Imports necessary libraries, including `asyncio`, `os`, `json`, `typing`, `dotenv`, `mcp`, and `google.genai`.
2.  **Configuration:** Loads environment variables (likely including the Gemini API key) from a `.env` file and server parameters from a `mcp-server-config.json` file. The server parameters include the command, arguments, and environment variables needed to start the server.
3.  **`GeminiMCPClient` Class:**
    *   `__init__`: Initializes the client, creates a Gemini client using the API key, and prepares an `AsyncExitStack` for managing resources.
    *   `connect_to_server`: Establishes a connection to the server using `stdio_client` from the `mcp` library. It initializes a `ClientSession` to manage communication and retrieves the available tools from the server.
    *   `process_query`: This is the core function for handling user queries. It sends the query to the Gemini API, configured to use the tools provided by the server. If Gemini's response includes function calls (tool calls), it calls the corresponding tools on the server using `session.call_tool`. The results from the tool calls are then sent back to Gemini to refine the response.
    *   `chat_loop`: Runs an interactive chat loop. It takes user input, sends it to `process_query`, and prints Gemini's response.
    *   `cleanup`: Closes the connection to the server and releases resources.
4.  **`main` Function:** Creates an instance of `GeminiMCPClient`, connects to the server, runs the chat loop, and ensures cleanup.
5.  **Execution:** The `if __name__ == "__main__":` block ensures that the `main` function is executed when the script is run.

In essence, this code sets up a client that connects to a server providing a set of tools. It then uses the Gemini API to create a chatbot that can use these tools to answer user queries. The MCP protocol is used to communicate with the server and call the tools.

**User**:

## References:
https://github.com/philschmid/gemini-samples/blob/main/examples/gemini-mcp-example.ipynb
https://ai.google.dev/gemini-api/docs/function-calling?example=meeting
https://modelcontextprotocol.io/quickstart/client
https://googleapis.github.io/python-genai/