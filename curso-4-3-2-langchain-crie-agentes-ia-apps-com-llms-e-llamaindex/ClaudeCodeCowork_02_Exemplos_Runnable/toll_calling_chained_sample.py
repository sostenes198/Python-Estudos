from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────
# Tools disponíveis
#
# Cenário: usuário pergunta se deve sair de casa.
# O agente pode encadear:
#   1. buscar_clima     → descobre o tempo
#   2. buscar_eventos   → descobre o que está acontecendo na cidade
#   3. recomendar_roupa → com base no clima, sugere o que vestir
#
# O LLM decide sozinho quais chamar e em que ordem.
# ─────────────────────────────────────────────────

@tool
def buscar_clima(cidade: str) -> dict:
    """Retorna temperatura e condição climática atual de uma cidade."""
    base = {
        "belo horizonte": {"temperatura_c": 20, "condicao": "parcialmente nublado", "chuva": False},
        "curitiba":        {"temperatura_c": 10, "condicao": "frio e chuvoso",       "chuva": True},
    }
    return base.get(cidade.lower(), {"erro": f"Cidade '{cidade}' não encontrada."})


@tool
def buscar_eventos(cidade: str) -> list:
    """Retorna lista de eventos acontecendo hoje na cidade."""
    base = {
        "belo horizonte": [
            {"nome": "Feira de artesanato",   "local": "Praça da Liberdade", "gratuito": True},
            {"nome": "Show de jazz",           "local": "Palácio das Artes",  "gratuito": False},
        ],
        "curitiba": [
            {"nome": "Exposição de fotografia", "local": "Museu Oscar Niemeyer", "gratuito": True},
        ],
    }
    return base.get(cidade.lower(), [])


@tool
def recomendar_roupa(temperatura_c: int, chuva: bool) -> dict:
    """Recomenda o que vestir com base na temperatura e se está chovendo."""
    if temperatura_c <= 12:
        roupa = "casaco grosso e cachecol"
    elif temperatura_c <= 18:
        roupa = "jaqueta leve ou moletom"
    else:
        roupa = "camiseta e calça leve"

    acessorio = "guarda-chuva" if chuva else "óculos de sol"

    return {"roupa": roupa, "acessorio": acessorio}


# ─────────────────────────────────────────────────
# LLM com todas as tools vinculadas
# ─────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
llm_com_tools = llm.bind_tools([buscar_clima, buscar_eventos, recomendar_roupa])

TOOLS_MAP = {
    "buscar_clima":     buscar_clima,
    "buscar_eventos":   buscar_eventos,
    "recomendar_roupa": recomendar_roupa,
}

# ─────────────────────────────────────────────────
# Loop do agente
#
# Fica rodando até o LLM parar de chamar tools
# e devolver uma resposta final em texto.
# ─────────────────────────────────────────────────

def executar_tools(tool_calls: list) -> list[ToolMessage]:
    resultados = []
    for tc in tool_calls:
        print(f"    🔧 chamando : {tc['name']}({tc['args']})")
        resultado = TOOLS_MAP[tc["name"]].invoke(tc["args"])
        print(f"    📦 resultado: {resultado}\n")
        resultados.append(ToolMessage(
            content=str(resultado),
            tool_call_id=tc["id"]
        ))
    return resultados


def agente(pergunta: str) -> str:
    print(f"\n{'=' * 55}")
    print(f"  Pergunta: {pergunta}")
    print(f"{'=' * 55}\n")

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Você é um assistente pessoal que ajuda o usuário a decidir o que fazer. "
         "Use as tools disponíveis para coletar as informações necessárias antes de responder. "
         "Encadeie as tools conforme precisar — não responda sem ter os dados completos."),
        ("human", "{input}"),
    ])

    # histórico de mensagens — começa só com o prompt inicial
    mensagens: list[BaseMessage] = prompt.invoke({"input": pergunta}).messages

    turno = 1
    while True:
        print(f"[Turno {turno}] Consultando LLM...\n")
        resposta: AIMessage = llm_com_tools.invoke(mensagens)

        # LLM não chamou nenhuma tool → chegou na resposta final
        if not resposta.tool_calls:
            print(f"[Turno {turno}] LLM encerrou o loop — resposta final pronta.\n")
            return resposta.content

        # LLM quer chamar tools → executa e adiciona os resultados ao histórico
        print(f"[Turno {turno}] LLM quer chamar {len(resposta.tool_calls)} tool(s):\n")
        tool_messages = executar_tools(resposta.tool_calls)

        # acumula no histórico: resposta do LLM + resultados das tools
        mensagens += [resposta] + tool_messages
        turno += 1


# ─────────────────────────────────────────────────
# Testes
# ─────────────────────────────────────────────────

# Deve encadear: buscar_clima → recomendar_roupa → resposta
resposta = agente("O que devo vestir para sair hoje em Curitiba?")
print(f"RESPOSTA FINAL:\n{resposta}\n")


# Deve encadear: buscar_clima → buscar_eventos → recomendar_roupa → resposta
resposta = agente("Tem algo legal para fazer hoje em BH?")
print(f"RESPOSTA FINAL:\n{resposta}\n")