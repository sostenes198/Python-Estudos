"""Simple MCP client/server proof of concept for log & progress notifications.

No Claude/LLM involved on purpose: this just shows the raw MCP mechanics —
a client calling a tool on `mcp_server.py` and printing the log messages and
progress updates the server streams back while it works.

Run:
    poetry run python cli_poc.py "archaeology"
"""

import asyncio
import sys
from pathlib import Path

from mcp.types import LoggingMessageNotificationParams

from mcp_client import MCPClient

SERVER_SCRIPT = Path(__file__).resolve().parent / "mcp_server.py"


async def logging_callback(params: LoggingMessageNotificationParams) -> None:
    print(f"[{params.level}] {params.data}")


async def print_progress_callback(
    progress: float, total: float | None, message: str | None
) -> None:
    if total is not None:
        percentage = (progress / total) * 100
        print(f"Progress: {progress}/{total} ({percentage:.1f}%) {message or ''}")
    else:
        print(f"Progress: {progress} {message or ''}")


async def run(topic: str) -> None:
    async with MCPClient(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        logging_callback=logging_callback,
    ) as client:
        result = await client.call_tool(
            "research",
            {"topic": topic},
            progress_callback=print_progress_callback,
        )

        print("\n--- Report ---\n")
        for item in result.content:
            if hasattr(item, "text"):
                print(item.text)


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "archaeology"
    asyncio.run(run(topic))
