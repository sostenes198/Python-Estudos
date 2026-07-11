"""MCP server that demonstrates log and progress notifications.

Exposes a single `research` tool that looks up a topic on Wikipedia while
reporting its progress through `Context.info()` (log messages) and
`Context.report_progress()` (progress updates), exactly like the pattern
taught in the "Log and progress notifications" lesson.

Manual testing with the MCP Inspector:
    npx @modelcontextprotocol/inspector poetry run python mcp_server.py
"""

import asyncio
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

mcp = FastMCP("WikipediaResearch", log_level="ERROR")

WIKIPEDIA_SEARCH_API = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
USER_AGENT = "mcp-log-progress-demo/1.0 (Anthropic Academy exercise)"


def _http_get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def _search_wikipedia(topic: str) -> str:
    query = urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": topic,
            "format": "json",
            "srlimit": 1,
        }
    )
    try:
        data = _http_get_json(f"{WIKIPEDIA_SEARCH_API}?{query}")
    except urllib.error.URLError as e:
        raise ValueError(f"Could not reach Wikipedia: {e}") from e

    hits = data.get("query", {}).get("search", [])
    if not hits:
        raise ValueError(f"No Wikipedia article found for '{topic}'")
    return hits[0]["title"]


def _fetch_summary(title: str) -> dict[str, Any]:
    url = WIKIPEDIA_SUMMARY_API.format(title=urllib.parse.quote(title))
    return _http_get_json(url)


@mcp.tool(
    name="research",
    description="Research a topic on Wikipedia and write a short report",
)
async def research(
    topic: str = Field(description="Topic to research"),
    *,
    context: Context,
) -> str:
    await context.info(f"About to research '{topic}'...")
    await context.report_progress(5, 100, "Searching Wikipedia")
    title = await asyncio.to_thread(_search_wikipedia, topic)

    await context.info(f"Found article '{title}'. Fetching summary...")
    await context.report_progress(35, 100, "Fetching article summary")
    summary = await asyncio.to_thread(_fetch_summary, title)

    await context.info("Analyzing content...")
    await context.report_progress(65, 100, "Analyzing content")

    await context.info("Writing report...")
    await context.report_progress(85, 100, "Writing report")
    page_url = summary.get("content_urls", {}).get("desktop", {}).get("page", "")
    report = (
        f"# {summary.get('title', title)}\n\n"
        f"{summary.get('extract', 'No summary available.')}\n\n"
        f"Source: {page_url}"
    )

    await context.report_progress(100, 100, "Done")
    return report


if __name__ == "__main__":
    mcp.run(transport="stdio")
