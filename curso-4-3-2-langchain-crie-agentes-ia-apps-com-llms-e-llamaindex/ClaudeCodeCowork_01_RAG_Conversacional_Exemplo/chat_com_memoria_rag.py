"""
=============================================================
  CHAT CONVERSACIONAL COM MEMÓRIA RAG - EXEMPLO DIDÁTICO
=============================================================

O QUE ESSE SCRIPT FAZ:
  1. Mantém um histórico de conversa salvo num banco vetorial (ChromaDB)
  2. A cada mensagem do usuário, busca os turnos mais RELEVANTES
     semanticamente — não os mais recentes, os mais RELEVANTES
  3. Injeta só esses trechos no contexto da LLM
  4. Isso permite conversas longas sem explodir o context window

DEPENDÊNCIAS:
  pip install chromadb sentence-transformers groq python-dotenv

MODELO DE EMBEDDING:
  Usa "all-MiniLM-L6-v2" — roda LOCAL, sem custo, sem API externa.
  É um modelo leve e eficiente para português e inglês.
"""

import os
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# =============================================================
# CONFIGURAÇÃO INICIAL
# =============================================================

# Cliente da LLM (Groq)
cliente_llm = Groq(api_key=os.getenv("API_KEY_GROK"))
MODELO_LLM = os.getenv("LLM_MODEL")

# Modelo de embedding — roda localmente, sem custo
# Na primeira execução, ele baixa o modelo (~90MB)
print("⏳ Carregando modelo de embedding (pode demorar na 1ª vez)...")
modelo_embedding = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Modelo de embedding carregado!\n")

# Banco vetorial em memória (para exemplo didático)
# Em produção: chromadb.PersistentClient(path="./banco_vetorial")
cliente_db = chromadb.Client()
colecao = cliente_db.create_collection(
    name="historico_conversa",
    # Usando distância de cosseno — mede similaridade semântica
    metadata={"hnsw:space": "cosine"}
)

# Quantos turnos relevantes recuperar do banco a cada busca
N_RESULTADOS = 3


# =============================================================
# FUNÇÕES PRINCIPAIS
# =============================================================

def gerar_embedding(texto: str) -> list[float]:
    """
    Converte texto em vetor numérico usando o modelo local.

    Exemplo:
        "computador não liga" → [0.82, 0.14, 0.67, 0.33, ...]

    Textos com significado parecido geram vetores parecidos.
    É isso que permite encontrar "problema voltou" quando
    o banco tem "computador com defeito".
    """
    vetor = modelo_embedding.encode(texto)
    return vetor.tolist()


def salvar_turno(numero: int, pergunta: str, resposta: str):
    """
    Salva um turno completo da conversa no banco vetorial.

    PONTO-CHAVE DIDÁTICO:
    Salvamos um DOCUMENTO RICO, não a frase isolada.
    Isso é crucial para a busca semântica funcionar bem.

    Exemplo do que é salvo:
        "Turno 3 | Usuário: meu computador Dell não liga
         Assistente: Vamos verificar a fonte de alimentação..."

    Quando o usuário disser "o problema voltou", a busca
    encontrará ESSE documento porque ambos pertencem ao
    universo semântico de "problema técnico com computador".
    """
    # Monta documento rico em contexto
    documento = f"Turno {numero} | Usuário: {pergunta} | Assistente: {resposta}"

    # Gera o embedding desse documento
    vetor = gerar_embedding(documento)

    # Salva no ChromaDB: texto + vetor + id único
    colecao.add(
        documents=[documento],
        embeddings=[vetor],
        ids=[f"turno_{numero}"]
    )

    print(f"   💾 Turno {numero} salvo no banco vetorial")
    print(f"   📐 Primeiros 5 valores do vetor: {[round(v, 4) for v in vetor[:5]]}...\n")


def buscar_contexto_relevante(pergunta_atual: str) -> str:
    """
    Busca os turnos mais SEMANTICAMENTE SIMILARES à pergunta atual.

    Como funciona internamente:
    1. Converte a pergunta em vetor
    2. Compara com TODOS os vetores no banco (similaridade de cosseno)
    3. Retorna os N mais próximos

    Similaridade de cosseno:
        1.0 = textos idênticos em significado
        0.8 = textos muito relacionados
        0.2 = textos sem relação
    """
    # Se o banco ainda está vazio (primeiras mensagens), retorna vazio
    if colecao.count() == 0:
        return ""

    # Gera o vetor da pergunta atual
    vetor_pergunta = gerar_embedding(pergunta_atual)

    # Quantos resultados retornar (não pode ser mais que o total no banco)
    n = min(N_RESULTADOS, colecao.count())

    # Busca os N documentos mais similares
    resultado = colecao.query(
        query_embeddings=[vetor_pergunta],
        n_results=n,
        include=["documents", "distances"]
    )

    documentos = resultado["documents"][0]
    distancias = resultado["distances"][0]

    # Monta o bloco de contexto com score de similaridade visível
    print(f"\n   🔍 Buscando contexto relevante para: '{pergunta_atual}'")
    linhas = []
    for doc, dist in zip(documentos, distancias):
        # Distância de cosseno: 0 = idêntico, 2 = oposto
        # Convertemos para similaridade: 1 - distância
        similaridade = round(1 - dist, 3)
        print(f"   📌 Similaridade {similaridade} → {doc[:80]}...")
        linhas.append(f"[Similaridade: {similaridade}] {doc}")

    return "\n".join(linhas)


def chamar_llm(pergunta: str, contexto: str) -> str:
    """
    Chama a LLM com a pergunta atual + contexto recuperado do banco.

    PONTO-CHAVE DIDÁTICO:
    O array 'messages' tem APENAS a mensagem atual.
    O histórico relevante vai no 'system', não no array.
    Isso mantém o context window sempre controlado.
    """
    # Monta o system prompt com o contexto recuperado
    if contexto:
        system_prompt = f"""Você é um assistente de suporte técnico prestativo.

Histórico relevante desta conversa (recuperado por similaridade semântica):
---
{contexto}
---

Use esse histórico para entender referências vagas do usuário como
"o problema voltou", "aquele erro", "como falei antes", etc.
Responda de forma clara e objetiva."""
    else:
        system_prompt = """Você é um assistente de suporte técnico prestativo.
Responda de forma clara e objetiva."""

    # Chamada para a LLM — note: messages tem SÓ a pergunta atual
    resposta = cliente_llm.chat.completions.create(
        model=MODELO_LLM,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pergunta}
        ],
        max_tokens=512,
        temperature=0.7
    )

    return resposta.choices[0].message.content


def processar_mensagem(numero_turno: int, pergunta: str) -> str:
    """
    Orquestra todo o fluxo RAG para uma mensagem:

    1. Busca contexto relevante no banco vetorial
    2. Chama a LLM com pergunta + contexto
    3. Salva o novo turno no banco
    4. Retorna a resposta
    """
    # PASSO 1: Recuperar contexto relevante do banco
    contexto = buscar_contexto_relevante(pergunta)

    # PASSO 2: Chamar a LLM
    resposta = chamar_llm(pergunta, contexto)

    # PASSO 3: Salvar esse turno no banco para uso futuro
    salvar_turno(numero_turno, pergunta, resposta)

    return resposta


# =============================================================
# LOOP PRINCIPAL DO CHAT
# =============================================================

def iniciar_chat():
    print("=" * 60)
    print("  CHAT COM MEMÓRIA RAG")
    print("  Modelo LLM  : Groq ", MODELO_LLM)
    print("  Embeddings  : all-MiniLM-L6-v2 (local)")
    print("  Banco vetorial: ChromaDB (em memória)")
    print("=" * 60)
    print("\nDica: tente mencionar algo de forma vaga depois de alguns")
    print("turnos, como 'o problema voltou' ou 'e aquele erro?'")
    print("\nDigite 'sair' para encerrar.\n")

    turno = 0

    while True:
        pergunta = input("Você: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("\nEncerrando chat. Até logo!")
            break

        print(f"\n{'─' * 50}")

        resposta = processar_mensagem(turno, pergunta)

        print(f"\n🤖 Assistente: {resposta}")
        print(f"{'─' * 50}\n")

        turno += 1

        # Mostra estado atual do banco a cada 3 turnos
        if turno % 3 == 0:
            print(f"   📊 Banco vetorial: {colecao.count()} turnos armazenados\n")


if __name__ == "__main__":
    iniciar_chat()
