
from functools import cache
from langchain_core.vectorstores import VectorStore

from factory.factory_util import model_to_module_and_class
from factory.llm_factory import get_default_embeddings
from service.configloader import deep_get, settings
import logging

logger = logging.getLogger(__name__)


#
# vectorstore instance and its setup
#

@cache
def get_vectorstore() -> VectorStore:
    # Read config
    config_vectorstore = deep_get(settings, "config.common.databases.vectorstore")
    module_and_class = deep_get(config_vectorstore, "class")
    (module_name, class_name) = model_to_module_and_class(module_and_class)
    class_kwargs = deep_get(config_vectorstore, "args")
    embedding_function_arg_name = deep_get(config_vectorstore, "embedding_function_arg_name")

    # Add embedding function to class_kwargs
    if embedding_function_arg_name is not None:
        class_kwargs[embedding_function_arg_name] = get_default_embeddings()

    # Create instance
    try:
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
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Error in setup VectorStore: {config_vectorstore}: {e}", e)
        else:
            logger.error(f"Error in setup VectorStore: {config_vectorstore}: {e}")
        return None

