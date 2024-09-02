
from functools import cache
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from configloader import settings
import logging

logger = logging.getLogger(__name__)


#def get_default_llm_with_streaming() -> BaseChatModel:
#    return ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)

@cache
def get_default_llm_with_streaming() -> BaseChatModel:
    local_config = None
    try:
        local_config = settings.config.common.default_llm_with_streaming
        logger.debug(f"local_config: {local_config}")

        # get the first key in the dictionary
        class_name = list(local_config.keys())[0]
        class_args = local_config[class_name]
        logger.info(f"Setup LLM: {class_name}({class_args})")

        # instantiate the class (dynamic instantiation)
        return globals()[class_name](**local_config[class_name])
        #return ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)
    except Exception as e:
        logger.error(f"Error in get_default_llm_with_streaming() with config={local_config}: {e}", e)
        exit(1)

def get_default_llm_without_streaming() -> BaseChatModel:
    return ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=False)
