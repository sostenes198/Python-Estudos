"""Streamlit chat UI replicating the "Wikipedia Research Assistant" demo from
the Anthropic Academy lesson "Log and progress notifications".

Claude drives a tool-calling loop against the `research` MCP tool
(mcp_server.py). While the tool runs, the server's log and progress
notifications are streamed live into an `st.status` block so the user sees
exactly what's happening instead of a silent spinner.

Run:
    poetry run streamlit run streamlit_app.py
"""

import asyncio
import os
import sys
from pathlib import Path

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv
from mcp.types import LoggingMessageNotificationParams

from mcp_client import MCPClient

load_dotenv()

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
SERVER_SCRIPT = Path(__file__).resolve().parent / "mcp_server.py"

SYSTEM_PROMPT = (
    "You are a Wikipedia Research Assistant. When the user asks about a "
    "topic, call the `research` tool to gather information from Wikipedia, "
    "then write a clear, well-structured report summarizing what you found. "
    "Only call the tool once per topic."
)

SUGGESTIONS = [
    "Research and write a report on geotechnical engineering",
    "What are the key discoveries in quantum computing?",
    "Explain the history and impact of the Renaissance",
]

st.set_page_config(page_title="Wikipedia Research Assistant", page_icon="🔎")

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []
if "claude_messages" not in st.session_state:
    st.session_state.claude_messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


async def run_turn(user_text: str, assistant_container) -> str:
    tool_log: dict = {"lines": [], "widget": None}

    async def logging_callback(params: LoggingMessageNotificationParams) -> None:
        tool_log["lines"].append(f"`{params.level}` {params.data}")
        if tool_log["widget"] is not None:
            tool_log["widget"].markdown("\n\n".join(tool_log["lines"]))

    async with MCPClient(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        logging_callback=logging_callback,
    ) as mcp_client:
        tools_result = await mcp_client.list_tools()
        tools = [
            {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
            for t in tools_result
        ]

        messages = st.session_state.claude_messages + [
            {"role": "user", "content": user_text}
        ]
        client = Anthropic()
        final_text = ""

        while True:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                final_text = "\n".join(
                    b.text for b in response.content if b.type == "text"
                )
                break

            lead_text = "\n".join(
                b.text for b in response.content if b.type == "text"
            )
            if lead_text:
                assistant_container.markdown(lead_text)

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                with assistant_container.status(
                    f"🔧 {block.name}  ·  call", expanded=False
                ) as status:
                    tool_log["lines"] = []
                    tool_log["widget"] = status.empty()
                    progress_bar = status.progress(0)

                    async def progress_callback(
                        progress: float, total: float | None, message: str | None
                    ) -> None:
                        pct = int(progress if total is None else progress / total * 100)
                        progress_bar.progress(min(max(pct, 0), 100), text=message or "")

                    result = await mcp_client.call_tool(
                        block.name, block.input, progress_callback=progress_callback
                    )
                    status.update(
                        label=f"✅ {block.name}  ·  call",
                        state="error" if result.isError else "complete",
                    )

                text_content = "\n".join(
                    item.text for item in result.content if hasattr(item, "text")
                )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": text_content,
                        "is_error": result.isError,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        st.session_state.claude_messages = messages
        return final_text


st.title("Wikipedia Research Assistant")
st.caption(
    "Ask me to research any topic on Wikipedia. I'll gather information, "
    "analyze content, and create comprehensive reports for you."
)

for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.display_messages:
    st.write("Try commands like:")
    cols = st.columns(len(SUGGESTIONS))
    for col, suggestion in zip(cols, SUGGESTIONS):
        if col.button(suggestion, use_container_width=True):
            st.session_state.pending_prompt = suggestion
            st.rerun()

user_text = st.chat_input("Ask me anything...") or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if user_text:
    st.session_state.display_messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        assistant_container = st.container()
        final_text = asyncio.run(run_turn(user_text, assistant_container))
        assistant_container.markdown(final_text)

    st.session_state.display_messages.append(
        {"role": "assistant", "content": final_text}
    )
