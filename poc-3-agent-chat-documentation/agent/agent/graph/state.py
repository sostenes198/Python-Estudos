from langgraph.graph import MessagesState


class RagState(MessagesState):
    rewrite_count: int
