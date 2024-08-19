from langchain.schema import Document
from answer_service.generate_2 import generate_answer

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import logging
                           
import answer_service.retrieval_grader_1
from utils.string_util import str_limit

logger = logging.getLogger(__name__)


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


def generate9(state):
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

    # Prompt
    prompt = hub.pull("rlm/rag-prompt")
    logger.debug(f"prompt: {prompt}")
    # prompt: input_variables=['context', 'question'] metadata={'lc_hub_owner': 'rlm', 'lc_hub_repo': 'rag-prompt', 'lc_hub_commit_hash': '50442af133e61576e74536c6556cefe1fac147cad032f4377b60c436e6cdcb6e'} messages=[HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['context', 'question'], template="You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\nQuestion: {question} \nContext: {context} \nAnswer:"))]

    # LLM
    #llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0) # cheaper
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0) # cheaper

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
    generation = llm.invoke(messages)
        #{
        #"context": docs_context,
        #"question": question, 
        #"messages": messages})
    logger.info(f"generation: {generation}")



    #return {"documents": documents, "messages": messages, "generation": generation}
    return {"documents": documents, "generation": generation}

def generate2(state):
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
    generation = "Sorrrrry - I'don't know!!!" # generate_answer("", messages)
    #messages.add_message(generation)

    return {"documents": documents, "messages": messages, "generation": generation}


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
