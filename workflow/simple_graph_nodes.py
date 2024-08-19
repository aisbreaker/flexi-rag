from langchain.schema import Document
from answer_service.generate_2 import generate_answer


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state: generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    #generation = rag_chain.invoke({"context": documents, "question": question})
    generation = generate_answer(question)

    return {"documents": documents, "question": question, "generation": generation}

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
