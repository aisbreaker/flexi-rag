### Generate

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from answer_service.retrieval_grader_1 import docs, question

# Prompt
prompt = hub.pull("rlm/rag-prompt")


# LLM
#llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0) # cheaper
llm = ChatOpenAI(model_name="gpt-4o", temperature=0) # cheaper



# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

docs_context = format_docs(docs)
print("docs_context")
print(docs_context)

# Chain
rag_chain = prompt | llm | StrOutputParser()

# Run
generation = rag_chain.invoke({"context": docs_context, "question": question})
print("generation")
print(generation)