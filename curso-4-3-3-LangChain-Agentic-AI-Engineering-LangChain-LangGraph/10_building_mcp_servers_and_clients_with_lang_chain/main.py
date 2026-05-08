import asyncio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

load_dotenv()

llm = ChatOpenAI()

stdio_server_params = StdioServerParameters(
    command="python",
    args=[
        "/home/sostenes.souza/Repos/Estudos/Python-Estudos/curso-4-3-3-LangChain-Agentic-AI-Engineering-LangChain-LangGraph/10_building_mcp_servers_and_clients_with_lang_chain/servers/match_server.py"
    ]
)


async def main():
    print("Hello from mcp-crash-course!")

    async with stdio_client(stdio_server_params) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            print("Session initialized")
            tools = await load_mcp_tools(session)
            print(tools)

            agent = create_agent(llm, tools)

            result = await agent.ainvoke({"messages": [HumanMessage(content="What is 2 + 2")]})

            print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
