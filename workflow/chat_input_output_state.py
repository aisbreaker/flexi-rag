from typing import List, Optional
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage


class ChatInputOutputState(TypedDict):
    """
    Represents the state of our graph.
    The node-internal state is not included here.

    Attributes:
        messages_input: all messages inclusive questions, i.e. the full context of the chat conversation
        answer_output: LLM generation
        stream_generate_on_last_node: whether to stream the generation on the last node
    """

    # input: all messages inclusive questions, i.e. the full context of the chat conversation
    input_messages: list[AnyMessage]

    # output: LLM generation
    output_answer: Optional[str] # generation

    # configuration
    config_stream_generate_on_last_node: Optional[bool] = False
