from typing import List, Optional, Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import MessagesState
from langchain_core.messages import AnyMessage


class Question:
    """
    Represents the question that is relevant for this workflow.
    Usually the last question asked by the user.

    Attributes:
        message_index: The index of the message in the message list
        original_content: The content of the question, not yet enriched by document snippets
    """

    message_index: int
    original_content: str

class AnswerWorkflowGraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    # all messages, i.e. the full context of the chat conversation
    # ??? ... have the type "list". The `add_messages` function
    # ??? in the annotation defines how this state key should be updated
    # ??? (in this case, it appends messages to the list, rather than overwriting them)
    messages: list[AnyMessage]

    # The question that is relevant for this workflow
    question: Optional[Question]

    # documents that enrich the question
    documents: Optional[List[str]]
    generation: Optional[str]
    stream_generate_on_last_node: Optional[bool] = False
