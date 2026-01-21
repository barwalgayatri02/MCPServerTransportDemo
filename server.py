import json
import platform
import sys
import uuid
import base64
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv("../.env")

# ---------------- MCP TOOL ----------------

# Create an MCP server
mcp = FastMCP(
    name="Calculator",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
    stateless_http=True,
)


# Add a simple calculator tool
@mcp.tool()
def add_number(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# Password generator tool
@mcp.tool()
def generate_password() -> str:
    """Generate password using UUID + base64 + reverse string"""
    uid = uuid.uuid4().hex
    encoded = base64.b64encode(uid.encode()).decode()
    password = encoded[::-1]
    return password

# UTC time tool

@mcp.tool()
def current_time() -> str:
    """Get current server time (UTC)"""
    return datetime.now(timezone.utc).isoformat()

# ---------------- MCP RESOURCE ----------------

@mcp.resource(
    uri="system://details",
    name="System Details",
    description="Read-only system information",
    mime_type="application/json",
)
def get_system_details():
    return json.dumps({
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0]
    }, indent=2)


# ---------------- MCP PROMPT ----------------

@mcp.prompt()
def system_Prompt() -> str:
    return (
        "You have two tools:\n"
        "- add(a, b): use to add numbers.\n"
        "- generate_password(): use to generate a password.\n"
        "Do not compute results yourself.\n"
        "Always call the correct tool."
    )

# Run the server
if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    
    print(f"Running server with transport: {transport}")

    if transport not in ["stdio", "sse", "streamable-http"]:
        raise ValueError(
            "Invalid transport. Use one of: stdio | sse | streamable-http"
        )
        
    mcp.run(transport=transport)