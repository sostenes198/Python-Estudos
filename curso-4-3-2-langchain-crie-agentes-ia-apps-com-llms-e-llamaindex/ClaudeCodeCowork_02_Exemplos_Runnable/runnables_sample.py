from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableBranch,
    RunnableParallel,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import random
import json

load_dotenv()

def separador(titulo: str):
    print(f"\n{'=' * 50}")
    print(f"  {titulo}")
    print('=' * 50)


# ─────────────────────────────────────────────────
# 1. RunnableLambda — embrulha função Python
# ─────────────────────────────────────────────────
separador("1. RunnableLambda")

def dobrar(x):
    return x * 2

chain = RunnableLambda(dobrar)
print(chain.invoke(5))   # → 10
print(chain.invoke(21))  # → 42


# ─────────────────────────────────────────────────
# 2. RunnablePassthrough — passa sem modificar
# ─────────────────────────────────────────────────
separador("2. RunnablePassthrough")

chain = RunnablePassthrough()
print(chain.invoke({"input": "olá"}))
# → {"input": "olá"}


# ─────────────────────────────────────────────────
# 3. RunnablePassthrough.assign — adiciona chave nova
# ─────────────────────────────────────────────────
separador("3. RunnablePassthrough.assign")

chain = RunnablePassthrough.assign(
    dobrado=RunnableLambda(lambda x: x["numero"] * 2)
)
print(chain.invoke({"numero": 5}))
# → {"numero": 5, "dobrado": 10}


# ─────────────────────────────────────────────────
# 4. RunnableBranch — if/elif/else no pipe
# ─────────────────────────────────────────────────
separador("4. RunnableBranch")

chain = RunnableBranch(
    (lambda x: x["nota"] >= 7, RunnableLambda(lambda x: "aprovado")),
    (lambda x: x["nota"] >= 5, RunnableLambda(lambda x: "recuperação")),
    RunnableLambda(lambda x: "reprovado"),  # fallback
)

print(chain.invoke({"nota": 8}))  # → aprovado
print(chain.invoke({"nota": 6}))  # → recuperação
print(chain.invoke({"nota": 3}))  # → reprovado


# ─────────────────────────────────────────────────
# 5. RunnableParallel — executa em paralelo
# ─────────────────────────────────────────────────
separador("5. RunnableParallel")

chain = RunnableParallel(
    maiusculo=RunnableLambda(lambda x: x["texto"].upper()),
    tamanho=RunnableLambda(lambda x: len(x["texto"])),
)
print(chain.invoke({"texto": "olá"}))
# → {"maiusculo": "OLÁ", "tamanho": 3}


# ─────────────────────────────────────────────────
# 6. {"chave": chain} — atalho de RunnableParallel
# ─────────────────────────────────────────────────
separador('6. {"chave": chain} — atalho RunnableParallel')

chain = {
    "maiusculo": RunnableLambda(lambda x: x["texto"].upper()),
    "tamanho":   RunnableLambda(lambda x: len(x["texto"])),
}
# dict puro não tem .invoke(), precisa embrulhar
chain = RunnableParallel(**chain)
print(chain.invoke({"texto": "olá"}))
# → {"maiusculo": "OLÁ", "tamanho": 3}


# ─────────────────────────────────────────────────
# 7. .with_retry() — retenta em caso de erro
# ─────────────────────────────────────────────────
separador("7. with_retry")

tentativas = {"n": 0}

def api_instavel(x):
    tentativas["n"] += 1
    print(f"  tentativa {tentativas['n']}...")
    if tentativas["n"] < 3:       # falha nas 2 primeiras tentativas
        raise Exception("timeout")
    return "sucesso na 3ª tentativa!"

chain = RunnableLambda(api_instavel).with_retry(
    stop_after_attempt=5,
)
print(chain.invoke({}))


# ─────────────────────────────────────────────────
# 8. RunnableWithMessageHistory — memória de conversa
# ─────────────────────────────────────────────────
separador("8. RunnableWithMessageHistory")

chat = ChatOpenAI(model="gpt-3.5-turbo-0125")

prompt = ChatPromptTemplate.from_messages([
    # Define o comportamento/personalidade do LLM
    # Só aparece uma vez, no início — é o "contrato" com o modelo
    ("system", "Você é um assistente prestativo."),

    # Expande uma lista de mensagens no lugar
    # usado para injetar histórico de conversa
    # aceita lista de HumanMessage/AIMessage
    ("placeholder", "{historico}"),

    # Mensagem do usuário — a pergunta/input humano
    # {input} é uma variável que você preenche no .invoke()
    ("human", "{input}"),

    # Mensagem genérica — você controla tudo manualmente
    # recebe um BaseMessage diretamente, sem template
    # ("generic", alguma_mensagem),
])

# ai aparece quando você quer fazer few-shot — ensinar o modelo com exemplos de pergunta e resposta antes do input real:
# ChatPromptTemplate.from_messages([
#     ("system", "Você classifica sentimentos como positivo ou negativo."),
#
#     # exemplos para o modelo aprender o padrão
#     ("human",  "Adorei o produto!"),
#     ("ai",     "positivo"),
#     ("human",  "Péssima experiência."),
#     ("ai",     "negativo"),
#
#     # aí vem o input real
#     ("human", "{input}"),
# ])

historicos = {}

def pegar_historico(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in historicos:
        historicos[session_id] = InMemoryChatMessageHistory()
    return historicos[session_id]

chain_com_memoria = RunnableWithMessageHistory(
    prompt | chat | StrOutputParser(),
    pegar_historico,
    input_messages_key="input",
    history_messages_key="historico",
)

config = {"configurable": {"session_id": "usuario_1"}}

resposta1 = chain_com_memoria.invoke(
    {"input": "Meu nome é Sóstenes"},
    config=config
)
print(f"Turno 1: {resposta1}")

resposta2 = chain_com_memoria.invoke(
    {"input": "Qual é o meu nome?"},
    config=config
)
print(f"Turno 2: {resposta2}")
# → "Seu nome é Sóstenes"

# ─────────────────────────────────────────────────
# 9. role "tool" — resultado de tool calling
# ─────────────────────────────────────────────────
separador("9. role tool — tool calling")

# O fluxo de tool calling tem 3 etapas:
#
#  [HUMAN]  pergunta do usuário
#     ↓
#  [AI]     LLM decide chamar uma tool (tool_calls)
#     ↓
#  [TOOL]   resultado da tool (ToolMessage)
#     ↓
#  [AI]     LLM responde usando o resultado
#
# O prompt abaixo representa o momento DEPOIS que a tool
# já foi executada e antes do LLM dar a resposta final.

prompt_tool = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente que consulta dados externos."),
    ("human", "{input}"),
    ("placeholder", "{tool_results}"),  # injeta [AIMessage + ToolMessage]
])

# Simula o que teria acontecido:
# 1. LLM pediu para chamar a tool "buscar_clima"
# 2. Sua aplicação executou a tool e obteve o resultado
tool_results_simulados = [
    AIMessage(
        content="",  # LLM não respondeu em texto
        tool_calls=[{  # mas pediu para chamar a tool
            "id": "call_123",
            "name": "buscar_clima",
            "args": {"cidade": "Belo Horizonte"}
        }]
    ),
    ToolMessage(
        content=json.dumps({  # resultado da execução da tool
            "temperatura": "28°C",
            "condicao": "ensolarado",
            "umidade": "60%"
        }),
        tool_call_id="call_123"  # deve bater com o id acima
    ),
]

resultado = prompt_tool.invoke({
    "input": "Como está o clima em BH?",
    "tool_results": tool_results_simulados,
})

print("O que chega ao LLM na etapa final:\n")
for msg in resultado.messages:
    print(f"  [{msg.type.upper()}]")
    if msg.content:
        print(f"  conteúdo : {msg.content}")
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"  tool_call: {msg.tool_calls}")
    print()