from langchain_text_splitters import RecursiveCharacterTextSplitter

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
)


def chunk_markdown(text: str) -> list[str]:
    return _SPLITTER.split_text(text)
