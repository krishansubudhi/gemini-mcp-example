from typing import Any
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("fileops")

@mcp.tool("ls")
async def ls(path: str) -> str:
    """
    List files and directories in the given path."""
    output = ""
    with os.scandir(path) as it:
        for entry in it:
            is_file = entry.is_file()
            is_dir = entry.is_dir()
            is_symlink = entry.is_symlink()
            name = entry.name
            output += f"{name} {'(file)' if is_file else ''} {'(dir)' if is_dir else ''} {'(link)' if is_symlink else ''}\n"
    return output 
            
@mcp.tool("cat")
async def cat(path: str) -> str:
    """
    Read the contents of a file."""
    with open(path, "r") as f:
        return f.read()
    return "File not found"


@mcp.tool("grep")
async def grep(path: str, pattern: str) -> str:
    """
    Search for a pattern in a file and return the first matching line.
    """
    with open(path, "r") as f:
        for line in f:
            if pattern in line:
                return line
    return "Pattern not found"

@mcp.tool("grepdir")
async def grepdir(directory_path: str, pattern: str) -> str:
    """
    Search for a pattern in all files in a directory and return the first matching line.
    """
    output = ""
    with os.scandir(directory_path) as it:
        for entry in it:
            if entry.is_file():
                with open(entry.path, "r") as f:
                    for line in f:
                        if pattern in line:
                            output += f"{entry.name}: {line}\n"
                            break # stop after first match in each file
    return output if output else "Pattern not found"
    

@mcp.tool("mkdir")
async def mkdir(path: str) -> bool:
    """
    Create a directory.
    If the directory already exists, return True.
    """
    try:
        os.makedirs(path)
        return True
    except FileExistsError:
        return True
    except Exception as e:
        return False

@mcp.tool("write")
async def write(path: str, content: str) -> bool:
    """
    Write content to a file.
    If the file does not exist, it will be created.
    If the file exists, it will be overwritten.
    """
    # check if directory exists
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w") as f:
        f.write(content)
        return True
    return False


if __name__ == "__main__":
    # Initialize and run the server
    print("Starting FastMCP server for fileops...")
    mcp.run(transport='stdio')