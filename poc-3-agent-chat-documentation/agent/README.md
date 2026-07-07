# Outline RAG Agent

FastAPI service that keeps a MongoDB Atlas hybrid (vector + full-text) index in sync with
an Outline instance, and answers questions about it from a Slack DM using a LangGraph
agent with self-correction and Anthropic Citations.

## Setup

1. `poetry install`
2. Copy `.env.example` to `.env` and fill in real values (Anthropic, OpenAI, Mongo Atlas,
   Outline, Slack — see the root spec at
   `docs/superpowers/specs/2026-07-06-poc-agent-chat-documentation-design.md` for what each
   one is for).
3. In MongoDB Atlas, on the `outline_chunks` collection, create:
   - A **Vector Search** index named `vector_index` on the `embedding` field
     (1536 dimensions, similarity `cosine`).
   - An **Atlas Search** index named `text_index`, full-text on the `content` field.
4. Run locally: `poetry run uvicorn agent.main:app --reload --port 8000`.
5. Expose it publicly (same or a second Cloudflare Tunnel as the Outline stack) so Outline
   and Slack can reach `/webhooks/outline`, `/webhooks/slack/events`, and
   `/webhooks/slack/commands`.

## Hybrid search: manual RRF vs `$rankFusion`

`agent/retrieval/hybrid_retriever.py` combines the vector leg
(`similarity_search_with_score`) and the full-text leg (a raw `$search` Atlas Search
aggregation) by hand-rolling Reciprocal Rank Fusion in Python, instead of a single
aggregation pipeline. This was a deliberate choice, not an oversight:

- At the time this was built, there was no confirmed LangChain retriever for Atlas
  full-text search, so the fusion step is our own code rather than a library call.
- MongoDB Atlas also offers a native `$rankFusion` aggregation stage that does hybrid
  search (vector + text) server-side in one pipeline — but it requires a specific
  Atlas tier/version that a free M0 cluster (the likely choice for this POC) may not
  support.

**Future optimization, if your Atlas cluster/tier supports it:** replace the Python-side
fusion in `hybrid_retriever.py` with a single `$rankFusion` aggregation stage. Benefits:
one round-trip to Atlas instead of two separate queries, fusion computed server-side
(lower latency, no need to over-fetch and merge in the app), and less custom code to
maintain (`_vector_leg`/`_text_leg`/RRF-scoring logic in this file could mostly go away).
This is not required for the POC to work — it's an upgrade path once the cluster tier
allows it.

## Slack App setup

1. Create an app at https://api.slack.com/apps.
2. **OAuth & Permissions** → Bot Token Scopes: `chat:write`, `im:history`, `im:read`,
   `im:write`, `commands`. Install to workspace, copy the Bot User OAuth Token into
   `SLACK_BOT_TOKEN`.
3. **App Home** → enable the Messages Tab, check "Allow users to send Slash commands and
   messages from the messages tab".
4. **Event Subscriptions** → Request URL: `https://<tunnel-domain>/webhooks/slack/events`.
   Subscribe to bot event `message.im`.
5. **Slash Commands** → Create `/nova-conversa`, Request URL:
   `https://<tunnel-domain>/webhooks/slack/commands`.
6. **Basic Information** → copy the Signing Secret into `SLACK_SIGNING_SECRET`.

## Running the tests

`poetry run pytest -v` — all tests run against mocks/fakes; no real Mongo/Anthropic/OpenAI/
Slack/Outline credentials are required to run the suite (a local `mongod` is only needed
for `tests/test_mongo.py`).

## Manual end-to-end check (not automated)

1. Create/edit a document in an Outline Collection (e.g. "Billing").
2. Confirm a new chunk appears in `outline_chunks` within a few seconds.
3. DM the Slack app a question about that document; confirm the reply quotes the right
   content and links back to the Outline document.
4. Wait >1h (or manually backdate `conversation_sessions.last_message_at` in Mongo) and
   send another message; confirm the "conversa expirou" notice appears.
5. Run `/nova-conversa`; confirm the next message starts with no prior context.
