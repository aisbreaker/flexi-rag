from typing import Dict, Optional
from langchain.schema import Document
from answer_service.generate_2 import generate_answer

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage
from langgraph.graph import END, StateGraph, START
from workflow.graph_state import AnswerWorkflowGraphState

import logging
                           
import answer_service.retrieval_grader_1
from utils.string_util import str_limit
from workflow.graph_state import AnswerWorkflowGraphState

logger = logging.getLogger(__name__)


#########################
# THIS WILL BE OUR DEFAULT WORKFLOW
#########################



def create_workflow():
    """
    Create the workflow.
    
    Keep in mind that all the (complex) logic is in a single node.
    """
    workflow = StateGraph(AnswerWorkflowGraphState)

    # define the nodes
    workflow.add_node("generate_chat_answer", generate_chat_answer)  # actual logic

    # build graph
    workflow.add_edge(START, "generate_chat_answer")
    workflow.add_edge("generate_chat_answer", END)
 
    # compile
    app = workflow.compile()
    return app
