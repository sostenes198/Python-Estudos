# Log and progress notifications

Notes from the Anthropic Academy MCP course lesson "Log and progress
notifications", plus a working proof of concept.

Logging and progress notifications are simple to implement but make a huge
difference in user experience when working with MCP servers. They help users
understand what's happening during long-running operations instead of
wondering if something has broken.

When Claude calls a tool that takes time to complete — like researching a
topic or processing data — users typically see nothing until the operation
finishes. This can be frustrating because they don't know if the tool is
working or has stalled.

With logging and progress notifications enabled, users get real-time feedback
showing exactly what's happening behind the scenes: progress bars, status
messages, and detailed logs as the operation runs.

## How it works

In the Python MCP SDK, logging and progress notifications work through the
`Context` argument that's automatically provided to your tool functions. This
object gives you methods to communicate back to the client during execution:

```python
@mcp.tool(
    name="research",
    description="Research a given topic",
)
async def research(
    topic: str = Field(description="Topic to research"),
    *,
    context: Context,
):
    await context.info("About to do research...")
    await context.report_progress(20, 100)
    sources = await do_research(topic)

    await context.info("Writing report...")
    await context.report_progress(70, 100)
    results = await generate_report(sources)

    return results
```

The key methods:

- `context.info()` — send log messages to the client
- `context.report_progress()` — update progress with current and total values

### Client-side implementation

On the client side, you set up callback functions to handle these
notifications. The server emits these messages, but it's up to the client
application to decide how to present them to users:

```python
async def logging_callback(params: LoggingMessageNotificationParams):
    print(params.data)

async def print_progress_callback(
    progress: float, total: float | None, message: str | None
):
    if total is not None:
        percentage = (progress / total) * 100
        print(f"Progress: {progress}/{total} ({percentage:.1f}%)")
    else:
        print(f"Progress: {progress}")

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read,
            write,
            logging_callback=logging_callback,
        ) as session:
            await session.initialize()

            await session.call_tool(
                name="research",
                arguments={"topic": "archaeology"},
                progress_callback=print_progress_callback,
            )
```

You provide the logging callback when creating the client session, and the
progress callback when making individual tool calls. This gives you
flexibility to handle different types of notifications appropriately.

### Presentation options

How you present these notifications depends on your application type:

- **CLI applications** — simply print messages and progress to the terminal
- **Web applications** — use WebSockets, server-sent events, or polling to
  push updates to the browser
- **Desktop applications** — update progress bars and status displays in
  your UI

Remember that implementing these notifications is entirely optional. You can
choose to ignore them completely, show only certain types, or present them
however makes sense for your application. They're purely user experience
enhancements to help users understand what's happening during long-running
operations.

## This folder

A minimal, working version of the demo shown in the lesson (a "Wikipedia
Research Assistant"), split into three pieces:

- **`mcp_server.py`** — a `FastMCP` server exposing one tool, `research`,
  that looks up a topic on Wikipedia (real HTTP calls, no mocking) while
  emitting `context.info()` logs and `context.report_progress()` updates at
  each step: searching, fetching the summary, analyzing, writing the report.
- **`mcp_client.py`** — a thin async wrapper around `ClientSession`/
  `stdio_client`, mirroring `4-mcp/mcp_client.py` but adding the
  `logging_callback` / `progress_callback` plumbing.
- **`cli_poc.py`** — the simplest possible client/server proof of concept:
  no Claude involved, just a client that calls the `research` tool directly
  and prints every log line and progress update as they arrive.
- **`streamlit_app.py`** — a chat UI that reproduces the lesson's demo:
  Claude decides when to call `research`, and while the tool runs its log
  and progress notifications stream live into an `st.status` block (the
  "🔧 research · call" / "Show details" collapsible seen in the recording),
  instead of the UI just sitting on a spinner.

### Setup

This folder shares the environment, dependencies, and `.env` file defined at
the repository root — same as `4-mcp/`. From the repository root:

```bash
poetry install
```

Make sure `curso-4-9-anthropic-academy/.env` has `ANTHROPIC_API_KEY` and
`CLAUDE_MODEL` set (see `.env-sample`).

### Run the plain MCP client/server POC (no LLM)

```bash
cd 4-1-mcp-log-and-progress-notifications
poetry run python cli_poc.py "archaeology"
```

### Run the Streamlit chat demo

```bash
cd 4-1-mcp-log-and-progress-notifications
poetry run streamlit run streamlit_app.py
```

### Inspect the server directly

```bash
npx @modelcontextprotocol/inspector poetry run python 4-1-mcp-log-and-progress-notifications/mcp_server.py
```
