from functools import lru_cache

import anthropic

from agent.config import get_settings

_MODEL = "claude-sonnet-4-5"
_SYSTEM_PROMPT = (
    "Voce e um assistente que responde perguntas de engenharia e produto usando "
    "exclusivamente os documentos fornecidos. Nunca invente informacao que nao esteja "
    "nos documentos. Se os documentos nao tiverem a resposta, diga que nao encontrou "
    "isso na documentacao."
)


@lru_cache
def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=get_settings().anthropic_api_key)


def _dedupe_sources(sources: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped = []
    for source in sources:
        if source["source"] not in seen:
            seen.add(source["source"])
            deduped.append(source)
    return deduped


def generate_grounded_answer(question: str, chunks: list[dict]) -> tuple[str, list[dict]]:
    content: list[dict] = [
        {
            "type": "document",
            "source": {"type": "text", "media_type": "text/plain", "data": chunk["content"]},
            "title": chunk["title"],
            "citations": {"enabled": True},
        }
        for chunk in chunks
    ]
    content.append({"type": "text", "text": question})

    response = _get_client().messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    answer_text = ""
    cited_sources: list[dict] = []
    for block in response.content:
        if getattr(block, "type", None) != "text":
            continue
        answer_text += block.text
        for citation in getattr(block, "citations", None) or []:
            index = citation.document_index
            if 0 <= index < len(chunks):
                cited_sources.append({"source": chunks[index]["source"], "owner": chunks[index]["owner"]})

    if not cited_sources:
        cited_sources = [{"source": c["source"], "owner": c["owner"]} for c in chunks]

    return answer_text, _dedupe_sources(cited_sources)
