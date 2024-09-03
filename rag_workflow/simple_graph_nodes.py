from typing import Dict, Optional
from langchain.schema import Document
from rag_response_service.not_used_yet.generate_2 import generate_answer

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage

import logging
                           
import rag_response_service.document_retrieval_grader
from factory.llm_factory import get_default_llm_with_streaming, get_default_llm_without_streaming
from utils.string_util import str_limit
from rag_workflow.graph_state import AnswerWorkflowGraphState

logger = logging.getLogger(__name__)



#
# initial setup
#

llm_without_streaming = get_default_llm_without_streaming()
    # ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=False)
llm_with_streaming = get_default_llm_with_streaming()
    #ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)



#
# the actual LangGraph node(s)
#
def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state: generation, that contains LLM generation
    """
    print("---GENERATE---")
    messages = state["messages"]
    documents = state["documents"]

    # RAG generation
    #generation = rag_chain.invoke({"context": documents, "question": question})
    generation = generate_answer(messages, documents)

    return {"documents": documents, "question": question, "generation": generation}


async def generate_on_last_node(
        state: AnswerWorkflowGraphState,
        config: RunnableConfig
    ) -> Dict:

    """
    Generate answer

    Args:
        state (dict): The current graph state
        config (RunnableConfig): The current runnable configuration
             Note on Python < 3.11
             https://langchain-ai.github.io/langgraph/how-tos/streaming-tokens/
                "When using python 3.8, 3.9, or 3.10, please ensure you manually pass the RunnableConfig through to the llm when invoking it like so: llm.ainvoke(..., config)."

    Returns:
        state (dict): New key added to state: generation, that contains LLM generation
    """

    logger.info("---GENERATE---")
    messages = state["messages"]
    documents = state["documents"]
    streaming = state["stream_generate_on_last_node"]

    # Prompt
    prompt = hub.pull("rlm/rag-prompt")
    logger.debug(f"prompt: {prompt}")
    # prompt: input_variables=['context', 'question'] metadata={'lc_hub_owner': 'rlm', 'lc_hub_repo': 'rag-prompt', 'lc_hub_commit_hash': '50442af133e61576e74536c6556cefe1fac147cad032f4377b60c436e6cdcb6e'} messages=[HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['context', 'question'], template="You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\nQuestion: {question} \nContext: {context} \nAnswer:"))]

    # LLM
    if not streaming:
        llm = llm_without_streaming
    else:
        llm = llm_with_streaming

    # NOTE: this is where we're adding a tag that we'll be using later to filter the outputs of the final node for streaming-mode
    llm = llm.with_config(tags=["final_node"])


    # get context (docs)
    question = messages[-1]["content"]
    """
    relevant_docs = answer_service.retrieval_grader_1.get_relevant_documents(question)

    # Post-processing
    def format_docs(docs):
        for doc in docs:
            logger.debug(f"docs_context: {str_limit(doc.page_content)}")
        return "\n\n".join(doc.page_content for doc in docs)

    docs_context = format_docs(relevant_docs)

    logger.info(f"docs_context: {str_limit(docs_context)}")
    """

    # Chain
    #rag_chain = prompt | llm  # | StrOutputParser()
    #rag_chain = messages | llm

    # Run
    #generation = rag_chain.invoke({
    if not streaming:
        logger.info("llm invoke (not streaming)")

        # Note on Python < 3.11
        # https://langchain-ai.github.io/langgraph/how-tos/streaming-tokens/
        #   "When using python 3.8, 3.9, or 3.10, please ensure you manually pass the RunnableConfig through to the llm when invoking it like so: llm.ainvoke(..., config)."
        generation = llm.invoke(messages, config=config)
            #{
            #"context": docs_context,
            #"question": question, 
            #"messages": messages})
        logger.info(f"llm done: generation: {generation}")
    else:
        logger.info("llm invoke (streaming/async)")
        generation = await llm.ainvoke(messages, config=config) #, config)
        # We return a list, because this will get added to the existing list
        logger.info(f"llm await done: generation: {generation}")


    #return {"documents": documents, "messages": messages, "generation": generation}
    return {"documents": documents, "generation": generation}



def enrich_first_question_by_retrieved_documents(
        state: AnswerWorkflowGraphState,
        config: RunnableConfig
    ) -> Dict:
    """
    Identify the (first) question: it's the first user message of a chat

    Retrive documents relevant to the question
    and enrich the question with the retrieved documents

    Args:
        state (dict): The current graph state inclusive messages

    Returns:
        state (dict): Graph state with extended messages
    """

    logger.info("---ENRICH FIRST QUESTION BY RETRIEVED DOCUMENTS---")   

    # search the (first) question
    messages: list[AnyMessage] = state["messages"]
    index_of_first_question = get_index_of_the_first_question(messages)

    if index_of_first_question is None:
        # no question found: nothing to do/to changes
        return {}
    else:
        # get the question
        question = messages[index_of_first_question]["content"]
        logger.info(f"question: {question}")

        # enrich the question with the retrieved documents
        enriched_question = enrich_question_with_retrieved_documents(question, config)

        # update the question
        messages[index_of_first_question]["content"] = enriched_question

        return {"messages": messages}


def enrich_question_with_retrieved_documents(
    question: str,
    #documents: Optional[List[Document]],
    config: RunnableConfig
) -> str:
    """
    Retrieve documents relevant to the question
    and enrich the question with the retrieved documents

    Args:
        question (str): The question
        config (RunnableConfig): The current runnable configuration

    Returns:
        str: The enriched question
    """

    logger.info("---ENRICH QUESTION WITH RETRIEVED DOCUMENTS---")

    # get the relevant documents
    relevant_docs = answer_service.document_retrieval_grader.get_relevant_documents(question)

    # Post-processing
    def format_docs(docs):
        for doc in docs:
            logger.debug(f"docs_context: {str_limit(doc.page_content)}")
        return "\n\n".join(doc.page_content for doc in docs)

    docs_context = format_docs(relevant_docs)

    logger.info(f"docs_context: {str_limit(docs_context)}")

    # enrich the question with the retrieved documents
    enriched_question = f"{question}\n\n{docs_context}"

    return enriched_question


def get_index_of_the_first_question(messages: list[AnyMessage]) -> Optional[int]:
    """
    Identify the (first) question: it's the first user message of a chat

    Args:
        messages (list[AnyMessage]): The current list of messages

    Returns:
        int: Index of the first question, or None if no question is found
    """
    for i, message in enumerate(messages):
        if message["role"] == "user":
            # found the first question
            return i
    # no question found
    return None




### Edges ###

"""
def route_question(state):
    "
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    "

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
"""
