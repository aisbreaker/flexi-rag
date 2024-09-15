
from functools import cache

from factory.factory_util import call_function_or_constructor
from service.configloader import deep_get, settings
from langchain_core.document_loaders import BaseLoader

from rag_index_service.blob_parser_document_loader import BlobParserDocumentLoader
from rag_index_service.tools.default_blob_parser import DefaultBlobParser
from rag_index_service.tools.wget_blob_loader import WgetBlobLoader

import logging

logger = logging.getLogger(__name__)


#
# DocumentLoader instance and it's setup
#


@cache
def get_document_loader(url: str) -> BaseLoader:

    #
    # Attention: Configuration from yaml is NOT YET USED HERE!!!
    # TODO!!!
    #

    document_loader = BlobParserDocumentLoader(WgetBlobLoader(url), DefaultBlobParser()) 
    return document_loader

    """
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
    """
