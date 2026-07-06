# POC: Agente de chat no Slack com RAG sobre documentação do Outline

## Objetivo

Um bot de chat no Slack (DM 1:1, sem canais) que responde dúvidas de engenharia/produto
com base **exclusivamente** na documentação escrita no Outline (self-hosted). Toda vez que
um documento é criado, atualizado, publicado, arquivado ou apagado no Outline, um webhook
mantém a base vetorial no MongoDB Atlas sincronizada automaticamente. O bot nunca deve
inventar respostas fora do que está documentado, e deve sempre indicar de onde tirou a
informação (link do documento + time/produto responsável).

## Não-objetivos (fora de escopo do v1)

- Múltiplos workspaces do Slack ou múltiplas instâncias do Outline.
- Fila externa de mensageria (Celery/RQ) — `BackgroundTasks` do FastAPI é suficiente para o
  volume de um POC.
- `$rankFusion` nativo do Atlas (fica como otimização futura, se o cluster/tier suportar).
- Autenticação/autorização por usuário do Slack — qualquer pessoa no DM do bot recebe
  resposta com base em toda a documentação, sem filtro de permissão por time.
- Deploy em produção / LangGraph Platform — o grafo roda embutido no nosso próprio FastAPI,
  não via `langgraph up`/Agent Server.

## Arquitetura

```
Outline (self-hosted)  --webhook-->  Agent API (FastAPI)  --tool call-->  Mongo Atlas
       ^                                    |    ^                       (chunks + vector +
       |                                    |    |                        full-text index)
   Cloudflare Tunnel <--- mesma tunnel --->  |    +--> LangGraph checkpoints (thread memory)
       |                                    v
   Slack  <--events API / slash cmd-- Slack App --> Agent API --> Anthropic API (Claude + citations)
```

Um único serviço Python (`agent/`) expõe rotas HTTP atrás do mesmo túnel Cloudflare:
`/webhooks/outline` (ingestão), `/webhooks/slack/events` (chat via DM) e
`/webhooks/slack/commands` (slash command `/nova-conversa`). Todas respondem rápido (200) e
delegam trabalho pesado para uma `BackgroundTask`, exceto o slash command de reset, que é
rápido o suficiente para responder de forma síncrona.

### Estrutura de pastas

```
poc-3-agent-chat-documentation/
├── outline/
│   ├── docker-compose.yml      # outline + postgres + redis + minio (storage S3-compatible) + cloudflared
│   ├── .env.example
│   └── README.md               # setup: admin inicial, criar collections (times), configurar webhook
└── agent/
    ├── pyproject.toml          # poetry, python 3.14
    ├── .env.example
    ├── README.md                # inclui setup do Slack App (scopes, Events API, slash command)
    ├── agent/
    │   ├── main.py              # FastAPI app, monta os routers
    │   ├── config.py            # settings (pydantic-settings)
    │   ├── db/
    │   │   └── mongo.py         # client Mongo (motor/pymongo), coleções
    │   ├── webhooks/
    │   │   ├── outline.py       # POST /webhooks/outline
    │   │   ├── slack_events.py  # POST /webhooks/slack/events (message.im)
    │   │   └── slack_commands.py# POST /webhooks/slack/commands (/nova-conversa)
    │   ├── ingestion/
    │   │   ├── outline_client.py    # busca doc/collection via API Outline (fonte de verdade)
    │   │   ├── chunker.py           # split markdown-aware
    │   │   ├── vector_store.py      # upsert/delete no MongoDBAtlasVectorSearch
    │   │   └── pipeline.py          # orquestra: fetch → chunk → embed (OpenAI) → upsert/delete
    │   ├── retrieval/
    │   │   ├── hybrid_retriever.py  # vector + Atlas Search full-text, fundidos por RRF
    │   │   └── tools.py             # tool `search_outline_docs(query, team=None)`
    │   ├── graph/
    │   │   ├── state.py             # schema do estado (messages, retrieved_docs, rewrite_count)
    │   │   ├── nodes.py             # generate_query_or_respond, grade_documents, rewrite_question,
    │   │   │                        # generate_answer, no_context_found, on_error
    │   │   └── build.py             # monta o StateGraph, compila com MongoDBSaver
    │   ├── citations/
    │   │   └── anthropic_citations.py  # chama Anthropic com citations habilitado, extrai fontes
    │   └── chat/
    │       ├── session.py           # TTL de inatividade (1h) + reset de sessão (delete_thread)
    │       └── slack_client.py      # responde no Slack (chat.postMessage / resposta de slash command)
    └── tests/
```

## Fluxo de ingestão (Outline → RAG)

1. Outline dispara webhook (`documents.create` / `documents.update` / `documents.publish` /
   `documents.delete` / `documents.archive`) para `/webhooks/outline`.
2. Endpoint valida assinatura HMAC (secret configurado no Outline), responde `200`
   imediatamente e enfileira uma `BackgroundTask` com `{event, document_id}`.
3. Para create/update/publish: a task busca o documento **fresco** via API do Outline
   (`documents.info`) em vez de confiar no corpo do webhook — evita depender do formato do
   payload e lida bem com múltiplos eventos rápidos para o mesmo documento.
4. Resolve o `owner`: busca a Collection raiz do documento (`collections.info` pelo
   `collectionId`, com cache em memória) → `owner = collection.name` (ex.: "Billing", "Pay").
5. Chunking markdown-aware → embedding via OpenAI (`text-embedding-3-small`) → apaga os
   chunks antigos daquele `outline_document_id` e insere os novos (evita chunks órfãos de
   versões antigas quando o texto muda de tamanho).
6. Para delete/archive: remove todos os chunks daquele `outline_document_id`, sem precisar
   chamar a API.

## Fluxo de consulta (Slack DM → resposta)

O bot é um Slack App sem canais: conversa 1:1 via Messages Tab do App Home, evento
`message.im` (sem necessidade de @mention), ignorando mensagens com `bot_id` (evita loop).

1. Slack Events API dispara `message` (`channel_type == "im"`) para
   `/webhooks/slack/events` → valida assinatura, responde `200`, enfileira `BackgroundTask`.
2. **Gerenciamento de sessão** (`chat/session.py`), antes de rodar o grafo:
   - `thread_id` do LangGraph = `channel_id` da DM (cada usuário tem um canal IM fixo com o
     app — é uma conversa contínua só, mesmo que o Slack permita replies em thread dentro da
     DM; threads do Slack não criam uma sessão de memória separada).
   - Busca `last_message_at` em `conversation_sessions` para esse `channel_id`.
     - Se não existir **ou** já passou de 1h: chama `checkpointer.delete_thread(thread_id)`
       de forma defensiva (no-op seguro se não havia nada) — evita um caso onde o índice TTL
       do Mongo apaga o rastreador antes da checagem e a gente acha erroneamente que "nunca
       teve conversa", deixando um checkpoint antigo vivo.
     - Se havia sessão anterior de fato expirada, responde antes de tratar a pergunta:
       _"Nossa conversa anterior expirou por inatividade — começando um papo novo!"_.
   - Grava/atualiza `last_message_at = now()`.
3. Grafo (`graph/build.py`), StateGraph explícito compilado com `checkpointer=MongoDBSaver(...)`:
   - `generate_query_or_respond`: Claude decide se chama a tool `search_outline_docs` ou
     responde direto (perguntas de conversa não precisam buscar).
   - Se chamou a tool → `retrieve` (`ToolNode`) executa a busca híbrida (vector + Atlas
     Search) e retorna os chunks com `content` + `metadata` (link, owner, título).
   - `grade_documents`: faz uma chamada rápida ao LLM (structured output sim/não) avaliando
     se os chunks recuperados são de fato relevantes para a pergunta — não é um threshold
     estático sobre o score de busca, já que similaridade alta não garante relevância
     semântica real.
     - Relevante → `generate_answer`.
     - Não relevante → `rewrite_question` (reformula a busca) → volta para
       `generate_query_or_respond`.
     - Limite de 2 reformulações sem sucesso → `no_context_found`, responde algo como "não
       encontrei isso na documentação" em vez de arriscar inventar ou looping infinito.
   - `generate_answer`: monta os chunks retidos como blocos `document`/`search_result` com
     `citations: {enabled: true}` e chama o client Anthropic direto (fora da abstração de
     mensagens do LangChain, só neste passo) → resposta com trechos citados mapeados a
     `metadata.source`. Se o parsing das citations falhar, cai no fallback: lista simples dos
     `link`/`owner` dos chunks usados — nunca fica sem fonte.
   - Erro de API (Anthropic/OpenAI) em qualquer nó → `on_error`, responde "tive um problema
     técnico, tenta de novo" — nunca deixa o usuário sem resposta alguma.
4. Resposta enviada de volta na DM via `chat.postMessage`, usando o `thread_ts` do evento
   recebido se presente (para aparecer visualmente na mesma thread que o usuário usou — isso
   é só sobre onde a resposta aparece na UI, não afeta a memória, que é sempre por
   `channel_id`). Formato: texto + bloco "Fontes:" com links deduplicados. Cada turno grava
   dois documentos em `conversation_log` (auditoria): um com `role=user` (pergunta recebida)
   e um com `role=assistant` (resposta final + `sources[]`).

## Encerrar/resetar conversa: slash command `/nova-conversa`

- Configurado no Slack App (`api.slack.com/apps` → Slash Commands), Request URL apontando
  para `/webhooks/slack/commands`.
- Slack envia `application/x-www-form-urlencoded` (não JSON) com `channel_id`, `user_id`,
  `command`, `response_url`, assinado do mesmo jeito que os eventos (mesma Signing Secret,
  reaproveita o helper de verificação).
- Handler valida a assinatura e, como é uma operação rápida (sem chamada de LLM), responde
  **de forma síncrona**: chama `reset_session(channel_id)` — que executa
  `checkpointer.delete_thread(channel_id)` e remove o doc em `conversation_sessions` — e
  retorna `200` com `{"response_type": "ephemeral", "text": "Conversa encerrada! Pode me chamar quando quiser 👋"}`.
- `reset_session()` vive em `chat/session.py` e é reaproveitada tanto pelo reset manual
  quanto pelo caminho de expiração por inatividade (mesma lógica, dois gatilhos).

## Modelo de dados (MongoDB Atlas)

- **`outline_chunks`** — um documento por chunk:
  `{outline_document_id, chunk_index, content, embedding[1536], metadata: {source, title, owner, collection_id, updated_at}}`.
  - Índice **Atlas Vector Search** (`vector_index`) sobre `embedding`, cosine, 1536 dims.
  - Índice **Atlas Search** (`text_index`) full-text sobre `content` — perna léxica da
    busca híbrida (ver Stack).
- Coleções do checkpointer do LangGraph (`checkpoints`, `checkpoint_writes`) — criadas e
  geridas automaticamente pelo `MongoDBSaver`, chave `thread_id`. É essa a "memória ativa"
  que o agente lê para continuar a conversa.
- **`conversation_sessions`** — `{_id: channel_id, last_message_at: datetime}`, com índice
  TTL (`expireAfterSeconds=3600`) como limpeza passiva de higiene (não é o mecanismo que
  decide a expiração — isso é lógica ativa em `chat/session.py`, ver acima).
- **`conversation_log`** — trilha de auditoria simples (não é lida pelo agente):
  `{channel_id, role, text, sources[], created_at}`. Satisfaz "salvar o chat conversado no
  Slack" de forma legível/consultável, sem ser a fonte de verdade da memória (essa é o
  checkpointer).

## Stack e integrações

- **Framework do agente**: LangChain + LangGraph (`StateGraph` explícito, não o
  `create_agent`/`create_react_agent` de alto nível, porque precisamos do nó
  `grade_documents` que eles não expõem).
- **LLM**: Anthropic Claude via `langchain-anthropic` (`ChatAnthropic`) para o loop do grafo;
  chamada direta ao SDK `anthropic` apenas no passo de geração final, para habilitar
  Citations.
- **Embeddings**: OpenAI (`text-embedding-3-small`).
- **Vetor + busca híbrida**: `langchain-mongodb` (`MongoDBAtlasVectorSearch`,
  `similarity_search_with_score`) para a perna vetorial + uma agregação `$search` (Atlas
  Search) via `pymongo` para a perna full-text, combinadas por Reciprocal Rank Fusion
  implementada diretamente no código do agente (não existe hoje um retriever LangChain
  dedicado para full-text no Atlas, então a fusão é feita à mão em vez de depender de uma
  classe não confirmada como `EnsembleRetriever`).
- **Memória de conversa**: `langgraph-checkpoint-mongodb` (`MongoDBSaver`/`AsyncMongoDBSaver`),
  chave `thread_id = channel_id` da DM.
- **Exposição pública**: Cloudflare Tunnel (container `cloudflared` no `docker-compose` do
  Outline), URL estável sem custo, cobre tanto o webhook do Outline quanto o do Slack.
- **Auth do Outline self-hosted**: email/senha (mais simples, sem exigir Slack App de OAuth
  para login).
- **Slack App**: Messages Tab habilitada (DM sem @mention), evento `message.im`, slash
  command `/nova-conversa`, scopes `chat:write`, `im:history`, `im:read`, `im:write`,
  `commands`.

## Tratamento de erros / edge cases

- **Assinatura inválida** (HMAC do Outline ou signing secret do Slack): responde `401` sem
  processar, loga a tentativa.
- **Webhooks duplicados/retry**: ingestão é idempotente (upsert por `outline_document_id`,
  delete-then-insert dos chunks); turno do Slack é idempotente por `event_id` (guarda os
  últimos N `event_id` processados para descartar duplicata — Slack reenvia se não receber
  `200` em 3s).
- **Outline API indisponível/rate limit** ao buscar o doc fresco: retry com backoff (2-3
  tentativas); se falhar, loga erro sem derrubar o processo (próximo webhook do mesmo doc
  tenta de novo).
- **Anthropic/OpenAI API erro ou timeout**: nó `on_error` no grafo, nunca deixa o usuário
  sem resposta.
- **Loop de rewrite sem achar contexto**: limite de 2 tentativas → `no_context_found`.
- **Mongo Atlas indisponível**: healthcheck próprio (`/health`); falha de ingestão no meio do
  processo é reprocessada no próximo webhook (idempotente).

## Testes

- Unitários (pytest) por módulo, com mocks: `chunker`, `hybrid_retriever` (mock dos
  retrievers do LangChain), `grade_documents`/`rewrite_question` (mock do LLM), parsing de
  citations, resolução de `owner` via collection, `chat/session.py` (TTL e reset).
- Teste de integração do grafo completo usando `InMemorySaver` (checkpointer em memória do
  próprio LangGraph, sem precisar de Mongo real) + `ChatAnthropic` fake/stub, cobrindo o
  caminho feliz e o caminho "sem contexto relevante".
- Sem teste automatizado ponta-a-ponta contra Outline/Slack/Atlas reais — validação manual do
  POC, documentada no README.

## Variáveis de ambiente / segredos

`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MONGODB_URI`, `OUTLINE_API_TOKEN`,
`OUTLINE_WEBHOOK_SECRET`, `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`. Nenhum valor real
hardcoded em nenhum arquivo do repositório — apenas `.env.example` com placeholders.
