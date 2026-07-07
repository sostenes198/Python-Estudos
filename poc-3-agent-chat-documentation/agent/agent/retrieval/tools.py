import json

from langchain_core.tools import tool

from agent.retrieval.hybrid_retriever import hybrid_search


@tool
def search_outline_docs(query: str, team: str | None = None) -> str:
    """Busca a documentacao interna (Outline) por trechos relevantes a pergunta.

    Use team para restringir a busca a um time/produto especifico (ex: "Billing",
    "Pay") quando a pergunta do usuario deixar isso claro. Retorna uma lista JSON de
    trechos com content, source (link), owner (time) e title.
    """
    results = hybrid_search(query, team=team)
    return json.dumps(results)
