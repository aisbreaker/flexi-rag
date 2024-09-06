### Question Re-writer

import logging
from async_lru import alru_cache
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import service.config as config
from factory.llm_factory import get_rewrite_question_llm

logger = logging.getLogger(__name__)


@alru_cache(maxsize=config.maxCachedQuestions)
async def rewrite_question_for_vectorsearch_retrieval(question: str) -> str:
    """
    Rewrite a question for vectorstore retrieval.
    """

    # LLM
    llm = get_rewrite_question_llm()

    # Prompt
    system = """You a question re-writer that converts an input question to a better version that is optimized \n 
         for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question.",
            ),
        ]
    )

    # Action
    question_rewriter = re_write_prompt | llm | StrOutputParser()
    updated_question = question_rewriter.invoke({"question": question})

    # Result
    logger.info(f"Updated question: '{question}' -> '{updated_question}'")
    return updated_question
