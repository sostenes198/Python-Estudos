from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────
# 1. Definição da tool customizada
#    @tool transforma a função em uma tool que o LLM
#    consegue "enxergar" e decidir chamar
# ─────────────────────────────────────────────────

@tool
def buscar_clima(cidade: str) -> dict:
    """Retorna o clima atual de uma cidade brasileira."""
    base_dados = {
        "belo horizonte": {"temperatura": "20°C", "condicao": "parcialmente nublado"},
        "curitiba":        {"temperatura": "10°C", "condicao": "frio e chuvoso"},
    }
    chave = cidade.lower().strip()
    if chave in base_dados:
        return base_dados[chave]
    return {"erro": f"Cidade '{cidade}' não encontrada na base de dados."}


# ─────────────────────────────────────────────────
# 2. LLM com a tool vinculada
#    .bind_tools() avisa ao LLM quais tools existem
#    e como chamá-las (nome, parâmetros, descrição)
# ─────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
llm_com_tools = llm.bind_tools([buscar_clima])


# ─────────────────────────────────────────────────
# 3. Prompt inicial
# ─────────────────────────────────────────────────

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de clima. Use as tools disponíveis para responder."),
    ("human", "{input}"),
])


# ─────────────────────────────────────────────────
# 4. Fluxo completo manual — passo a passo
#    para deixar claro o que acontece em cada etapa
# ─────────────────────────────────────────────────

def executar_tool(tool_call: dict) -> ToolMessage:
    """Recebe o pedido do LLM e executa a tool correspondente."""
    nome   = tool_call["name"]
    args   = tool_call["args"]
    id_    = tool_call["id"]

    print(f"  → tool chamada : {nome}")
    print(f"  → argumentos   : {args}")

    if nome == "buscar_clima":
        resultado = buscar_clima.invoke(args)
    else:
        resultado = {"erro": f"Tool '{nome}' desconhecida."}

    print(f"  → resultado    : {resultado}\n")

    return ToolMessage(
        content=str(resultado),
        tool_call_id=id_
    )


def agente_clima(pergunta: str) -> str:
    print(f"\n{'=' * 55}")
    print(f"  Pergunta: {pergunta}")
    print(f"{'=' * 55}\n")

    # ── Etapa 1: LLM decide se chama uma tool ──────────────
    print("[Etapa 1] Enviando pergunta ao LLM...\n")
    mensagens = prompt.invoke({"input": pergunta}).messages
    resposta_llm: AIMessage = llm_com_tools.invoke(mensagens)

    # ── Etapa 2: verifica se o LLM quer chamar alguma tool ──
    if not resposta_llm.tool_calls:
        print("[Etapa 2] LLM respondeu diretamente (sem tool):\n")
        return resposta_llm.content

    print(f"[Etapa 2] LLM quer chamar {len(resposta_llm.tool_calls)} tool(s):\n")

    # ── Etapa 3: executa cada tool pedida pelo LLM ──────────
    print("[Etapa 3] Executando tools...\n")
    tool_messages = [executar_tool(tc) for tc in resposta_llm.tool_calls]

    # ── Etapa 4: devolve tudo ao LLM para resposta final ────
    # histórico: pergunta original + pedido do LLM + resultados das tools
    print("[Etapa 4] Enviando resultados de volta ao LLM...\n")
    mensagens_completas = mensagens + [resposta_llm] + tool_messages
    resposta_final: AIMessage = llm.invoke(mensagens_completas)

    return resposta_final.content


# ─────────────────────────────────────────────────
# 5. Testes
# ─────────────────────────────────────────────────

# Teste 1 — cidade conhecida
print(agente_clima("Como está o clima em Belo Horizonte agora?"))

# Teste 2 — outra cidade conhecida
print(agente_clima("Tá frio em Curitiba hoje?"))

# Teste 3 — cidade desconhecida (erro da tool)
print(agente_clima("E o clima em Manaus?"))

# Teste 4 — pergunta sem necessidade de tool
print(agente_clima("Qual é a capital do Brasil?"))