# FileOps MCP Server and Gemini MCP Client

This project consists of two components:
1. **FileOps MCP Server**: A server to perform file operations using the Model Context Protocol (MCP).
2. **Gemini MCP Client**: A command-line chat client that interacts with the FileOps MCP Server and integrates with the Gemini API.

---


## FileOps MCP Server

The FileOps MCP Server provides tools to perform various file operations like listing files, reading file contents, searching patterns, creating directories, and writing to files.


```
cd fileops-mcp-server
```

### Set up instructions:

Install uv.
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create virtual env and sync

```
uv venv

source .venv/bin/activate

uv sync
```

---

## Gemini MCP Client

```
cd ../gemini-mcp-client
```
The Gemini MCP Client is a command-line chat client that integrates with the FileOps MCP Server and the Gemini API for enhanced functionality.


### Set up Instructions:

Set up virtual env and install deps

```
uv venv

source .venv/bin/activate

uv sync

```
Set up gemini

```
# Create .env file
touch .env

```
Add your key to .env file

```
GEMINI_API_KEY=<Your gemini key>
```

Add `.env` to `.gitignore`
```
echo ".env" >> .gitignore
```

Modify `mcp-server-config.json` and replace with your mcp server path and uv details.

Start the client application

```
python client.py
```



For detailed setup instructions and usage, refer to the [Gemini MCP Client README](./gemini-mcp-client/README.md).

---

## References:
- [Model Context Protocol Quickstart (Server)](https://modelcontextprotocol.io/quickstart/server)
- [Model Context Protocol Quickstart (Client)](https://modelcontextprotocol.io/quickstart/client)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs/function-calling?example=meeting)
- [Python GenAI SDK](https://googleapis.github.io/python-genai/)
- [Gemini MCP Example](https://github.com/philschmid/gemini-samples/blob/main/examples/gemini-mcp-example.ipynb)