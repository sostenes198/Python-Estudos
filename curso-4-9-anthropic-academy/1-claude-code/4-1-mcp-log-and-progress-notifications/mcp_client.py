"""Thin async wrapper around an MCP stdio client session.

Same shape as `4-mcp/mcp_client.py`, extended with a `logging_callback` so
callers can receive the server's log notifications, and a `progress_callback`
per tool call to receive progress notifications.
"""

import sys
import asyncio
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.session import LoggingFnT
from mcp.client.stdio import stdio_client
from mcp.shared.session import ProgressFnT


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
        logging_callback: Optional[LoggingFnT] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._logging_callback = logging_callback
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read, write, logging_callback=self._logging_callback)
        )
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized. Call connect() first."
            )
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(
        self,
        tool_name: str,
        tool_input: dict,
        progress_callback: Optional[ProgressFnT] = None,
    ) -> types.CallToolResult:
        return await self.session().call_tool(
            tool_name, tool_input, progress_callback=progress_callback
        )

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
async def main():
    async with MCPClient(
        command=sys.executable,
        args=["mcp_server.py"],
    ) as _client:
        pass


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
