Comando para subir inspector:  `npx @modelcontextprotocol/inspector poetry run python 4-mcp/mcp_server.py`
# MCP Chat

MCP Chat is a command-line interface application that enables interactive chat capabilities with AI models through the Anthropic API. The application supports document retrieval, command-based prompts, and extensible tool integrations via the MCP (Model Control Protocol) architecture.

## Prerequisites

- Python 3.9+
- Anthropic API Key

This project shares the environment, dependencies and `.env` file defined at the repository root (`curso-4-9-anthropic-academy/`) — it has no `pyproject.toml`, lockfile or `.env` of its own.

## Setup

### Step 1: Configure the environment variables

Edit the `.env` file at the repository root (`curso-4-9-anthropic-academy/.env`, see `.env-sample`) and verify that the following variables are set correctly:

```
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-5
```

### Step 2: Install dependencies

Dependencies (`anthropic`, `python-dotenv`, `mcp[cli]`, `prompt-toolkit`) are declared in the root `pyproject.toml` and managed with Poetry. From the repository root:

```bash
poetry install
```

### Step 3: Run the project

From within this directory (`4-mcp/`), using the shared Poetry environment:

```bash
poetry run python main.py
```

## Usage

### Basic Interaction

Simply type your message and press Enter to chat with the model.

### Document Retrieval

Use the @ symbol followed by a document ID to include document content in your query:

```
> Tell me about @deposition.md
```

### Commands

Use the / prefix to execute commands defined in the MCP server:

```
> /summarize deposition.md
```

Commands will auto-complete when you press Tab.

## Development

### Adding New Documents

Edit the `mcp_server.py` file to add new documents to the `docs` dictionary.

### Implementing MCP Features

To fully implement the MCP features:

1. Complete the TODOs in `mcp_server.py`
2. Implement the missing functionality in `mcp_client.py`

### Linting and Typing Check

There are no lint or type checks implemented.
