### Generate

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

import answer_service.retrieval_grader_1

def generate_answer(question):
    # Prompt
    prompt = hub.pull("rlm/rag-prompt")


    # LLM
    #llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0) # cheaper
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0) # cheaper

    # get context (docs)
    relevant_docs = answer_service.retrieval_grader_1.get_relevant_documents(question)

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    docs_context = format_docs(relevant_docs)
    print("docs_context")
    print(docs_context)

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    generation = rag_chain.invoke({"context": docs_context, "question": question})
    print("generation done, length:"+str(len(generation)))
    #print(generation)

    return generation
