
from functools import cache
from typing import Dict, Optional
from langchain_core.language_models.chat_models import BaseChatModel

from service.configloader import settings
import logging

logger = logging.getLogger(__name__)


#
# Specific LLM instances and their setup
#

@cache
def get_default_llm_without_streaming() -> BaseChatModel:
    config_llm_key = settings.config.rag_response_service["default_llm"]
    llm = setup_llm_for_config_llm_key(config_llm_key)
    logger.info(f"Setup done: config.rag_response_service.default_llm={llm}")
    return llm
@cache
def get_default_llm_with_streaming() -> BaseChatModel:
    config_llm_key = settings.config.rag_response_service["default_llm_with_streaming"]
    llm = setup_llm_for_config_llm_key(config_llm_key)
    logger.info(f"Setup done: config.rag_response_service.default_llm_with_streaming={llm}")
    return llm


def get_document_grader_llm() -> BaseChatModel:
    config_llm_key = settings.config.rag_response_service["document_grader_llm"]
    llm = setup_llm_for_config_llm_key(config_llm_key)
    logger.info(f"Setup done: config.rag_response_service.document_grader_llm={llm}")
    return llm


def get_rewrite_question_llm() -> BaseChatModel:
    config_llm_key = settings.config.rag_response_service["rewrite_question_llm"]
    llm = setup_llm_for_config_llm_key(config_llm_key)
    logger.info(f"Setup done: config.rag_response_service.rewrite_question_llm={llm}")
    return llm


#
# Helper functions for dynamic LLM setup
#

def setup_llm_for_config_llm_key(config_llm_key: str) -> Optional[BaseChatModel]:
    logger.info(f"Setup LLM from config_llm_key: {config_llm_key}")
    llm_config = settings.config.common.llms[config_llm_key]
    return setup_llm_for_config(config_llm_key=config_llm_key, llm_config=llm_config)

def setup_llm_for_config(
        config_llm_key: Optional[str],
        llm_config: Optional[Dict],
    ) -> BaseChatModel:
    """
    Setup LLM from config. Fails with error if not possible.

    Args:
        config_llm_key (str): LLM name (for logging purposes only)
        llm_config (dict): LLM configuration
        
    Returns:
        BaseChatModel: LLM instance, None in the case of an error
    """
    try:
        # TODO: remove access tokens before logging
        logger.info(f"Setup LLM: {config_llm_key}({llm_config})")

        # Pre-checks
        if llm_config is None:
            logger.error(f"Error in LLM setup: llm_config is None for {config_llm_key}")
            return None

        # Get the the parameters
        module_name = llm_config["module"]
        class_name = llm_config["class"]
        class_kwargs = llm_config["args"]

        # Instantiate the class (dynamic instantiation)
        import importlib
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        instance = class_(**class_kwargs)
        # Incomplete(!!!) alternavive would be:
        #   instance = globals()[class_name](**class_kwargs)
        #   instance = langchain_openai.ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)

        return instance

    except Exception as e:
        logger.debug(f"Error in setup LLM: {config_llm_key}({class_kwargs}): {e}", e)
        logger.error(f"Error in setup LLM: {config_llm_key}({class_kwargs}): {e}")
        return None
