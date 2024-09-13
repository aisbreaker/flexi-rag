
from functools import cache
from langchain_core.vectorstores import VectorStore

from factory.factory_util import call_function_or_constructor
from factory.llm_factory import get_default_embeddings
from service.configloader import deep_get, settings
import logging

logger = logging.getLogger(__name__)


#
# vectorstore instance and its setup
#

@cache
def get_vectorstore() -> VectorStore:
    # Start
    config_vectorstore = deep_get(settings, "config.common.databases.vectorstore")
    context_str_for_logging = f"Setup VectorStore: {config_vectorstore}"
    logger.info(context_str_for_logging)

    # Load config
    module_and_class            = deep_get(config_vectorstore, "class")
    class_kwargs                = deep_get(config_vectorstore, "args")
    embedding_function_arg_name = deep_get(config_vectorstore, "embedding_function_arg_name")

    # Add embedding function to class_kwargs
    if embedding_function_arg_name is not None:
        class_kwargs[embedding_function_arg_name] = get_default_embeddings()

    # Action: Create instance
    return call_function_or_constructor(module_and_class, class_kwargs, context_str_for_logging)
