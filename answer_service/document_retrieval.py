### Retrieval of (Graded) Documents

import logging
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.documents import Document

from answer_service.document_retrieval_grader import grade_documents_for_question
from factory.llm_factory import get_document_grader_llm
from index_service.build_index import get_vectorstore, get_vectorstore_retriever, vectorStoreRetriever
from utils.string_util import str_limit
from async_lru import alru_cache
import config

logger = logging.getLogger(__name__)

@alru_cache(maxsize=config.maxCachedQuestions)
async def get_relevant_documents(question: str) -> List[Document]:
    """Get relevant documents for a given question."""

    # Retrive documents
    vectorStore = get_vectorstore()
    docs = vectorStore.similarity_search(question, k=4)
    logger.debug("Found "+str(len(docs))+" docs in vectorstore (un-graded candidates)")
    # TODO: remove old code:
    #vectorStoreRetriever = get_vectorstore_retriever()
    #docs = vectorStoreRetriever.get_relevant_documents(question) # LangChainDeprecationWarning: The method `BaseRetriever.get_relevant_documents` was deprecated in langchain-core 0.1.46 and will be removed in 0.3.0. Use invoke instead.
    #docs = retriever.invoke({"question": question, "documents": docs})
    #docs = vectorStoreRetriever.get_relevant_documents(question)
    #docs = vectorStoreRetriever.invoke(input=question)

    # Grade the documents
    relevant_docs = await grade_documents_for_question(question, docs)
   
    # Result
    logger.info(f"found {str(len(relevant_docs))} relevant docs out of {str(len(docs))} candidates")
    return relevant_docs
