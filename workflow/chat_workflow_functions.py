from functools import lru_cache
from typing import Dict, Optional
from langchain.schema import Document
from answer_service.generate_2 import generate_answer

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage
from langgraph.graph import END, StateGraph, START
from workflow.chat_input_output_state import ChatInputOutputState
from workflow.graph_state import AnswerWorkflowGraphState

import logging
                           
import answer_service.retrieval_grader_1
from utils.string_util import str_limit
from workflow.graph_state import AnswerWorkflowGraphState

logger = logging.getLogger(__name__)

#########################
# THIS WILL BE THE LOGIC OF OUR DEFAULT WORKFLOW
#########################

#
# types
#
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
    enriched_content: Optional[str]

    def __init__(self, message_index: int, original_content: str, enriched_content: Optional[str]):
        self.message_index = message_index
        self.original_content = original_content
        self.enriched_content = enriched_content


#
# initial setup
#

#llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
llm_with_streaming = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)
llm_without_streaming = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=False)


def enrich_questions_with_retrieved_documents(
        messages: list[AnyMessage],
        config: RunnableConfig
    ) -> list[AnyMessage]:
    """
    Enrich questions in messages with retrieved documents

    Args:
        messages (list[AnyMessage]): The list of messages
        config (RunnableConfig): The current runnable configuration

    Returns:
        list[AnyMessage]: The updated list of messages
    """
    # identify questions
    questions = identify_questions(messages)
    # enrich the questions in messages
    for question in questions:
        # single question
        enriched_question = enrich_question_with_retrieved_documents(question, config)
        # set in messages
        messages[enriched_question.message_index]["content"] = enriched_question.enriched_content
    return messages

# settings
maxCachedQuestions = 128
vectorsearchEnabled = True
fulltextsearchEnabled = False
answerGradingEnabled = True
questionRewritingEnabled = True

def enrich_question_with_retrieved_documents(question: Question, config: RunnableConfig) -> Question:
    # anything to do?
    if not question.enriched_content:
        # yes
        question.enriched_content = enrich_question_str_with_retrieved_documents(question.original_content) #, config)    

    return question

@lru_cache(maxsize=maxCachedQuestions)
def enrich_question_str_with_retrieved_documents(
    question_str: str,
    #config: RunnableConfig
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
    relevant_docs = answer_service.retrieval_grader_1.get_relevant_documents(question_str)

    # Post-processing
    def format_docs(docs):
        for doc in docs:
            logger.debug(f"docs_context: {str_limit(doc.page_content)}")
        return "\n\n".join(doc.page_content for doc in docs)

    docs_context = format_docs(relevant_docs)

    logger.info(f"docs_context: {str_limit(docs_context)}")

    # enrich the question with the retrieved documents
    enriched_question = f"{question_str}\n\n{docs_context}"

    return enriched_question



def vectorsearch_document_retrieval():
    # TODO: implement
    return list()

def fulltextsearch_document_retrieval():
    # TODO: implement
    return list()

def grade_documents_for_question():
    # TODO: implement
    return list()

def transform_retrieval_question_for_vectorsearch_document_retrieval():
    # TODO: implement
    return list()

def transform_retrieval_question_for_fulltextsearch_document_retrieval():
    # TODO: implement
    return list()


def identify_questions(messages: list[AnyMessage]) -> list[Question]:
    """
    Identify questions in the messages

    Args:
        messages (list[AnyMessage]): The list of messages

    Returns:
        list[Question]: List of questions
    """   
    questions = list()
    # pick all user messages and make them questions
    for i, message in enumerate(messages):
        if message["role"] == "user":
            question = Question(
                message_index=i,
                original_content=message["content"],
                enriched_content=None)
            questions.append(question)
    return questions



#
# the actual LangGraph node(s)
#

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


    # add context to the question(s)
    messages = enrich_questions_with_retrieved_documents(messages, config)

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
