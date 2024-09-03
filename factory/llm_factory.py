
from functools import cache
from typing import Dict, Optional
from langchain_core.language_models.chat_models import BaseChatModel

from configloader import settings
import logging

logger = logging.getLogger(__name__)


#
# Specific LLM instances and their setup
#

@cache
def get_default_llm_without_streaming() -> BaseChatModel:
    llm_full_config = settings.config.common["default_llm"]
    return setup_llm_from_config(llm_full_config)

@cache
def get_default_llm_with_streaming() -> BaseChatModel:
    llm_full_config = settings.config.common["default_llm_with_streaming"]
    return setup_llm_from_config(llm_full_config)





#
# Helper functions for dynamic LLM setup
#

def setup_llm_from_config(llm_config: Optional[Dict]) -> Optional[BaseChatModel]:
    """
    Setup LLM from full config. Fails with error if not possible.

    Args:
        llm_config (dict): LLM full configuration
        
    Returns:
        BaseChatModel: LLM instance, None in the case of an error
    """
    # Pre-checks
    if llm_config is None:
        logger.error(f"Error in LLM setup: llm_long_config is None")
        return None
    llm_name = llm_config["name"]
    if llm_name is None:
        logger.error(f"Error in LLM setup: LLM 'name' is not configured")
        return None
    llm_config = llm_config[llm_name]
    if llm_config is None:
        logger.error(f"Error in LLM setup: no config found for LLM name='{llm_name}'")
        return None

    # Action
    return setup_llm_for_single_config(llm_config, llm_name)

def setup_llm_for_single_config(
        llm_config: Optional[Dict],
        llm_name: Optional[str]
    ) -> BaseChatModel:
    """
    Setup LLM from config. Fails with error if not possible.

    Args:
        llm_config (dict): LLM configuration
        llm_name (str): LLM name (for logging purposes only)
        
    Returns:
        BaseChatModel: LLM instance, None in the case of an error
    """
    try:
        # TODO: remove access tokens before logging
        logger.info(f"Setup LLM: {llm_name}({llm_config})")

        # Pre-checks
        if llm_config is None:
            logger.error(f"Error in LLM setup: llm_config is None for {llm_name}")
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
        logger.debug(f"Error in setup LLM: {llm_name}({class_kwargs}): {e}", e)
        logger.error(f"Error in setup LLM: {llm_name}({class_kwargs}): {e}")
        return None
