from typing import Iterator

from langchain_core.documents import Document
from langchain_core.documents.base import Blob
from langchain_community.document_loaders.base import BaseBlobParser
from langchain_community.document_loaders import BlobLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

import logging


logger = logging.getLogger(__name__)



class BlobParserDocumentLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, blobLoader: BlobLoader, blobParser: BaseBlobParser) -> None:
        """Initialize the loader with a blobLoader and a blobParser.

        The blobLoader is used to load the files that are then parsed by the blobParser.

        Args:
            blobLoader: the blobLoader to load the files that are then parsed
            blobParser: the blobParser to parse the loaded files
        """
        self.blobLoader = blobLoader
        self.blobParser = blobParser


    def lazy_load(self) -> Iterator[Document]:  # <-- Does not take any arguments
        """
        A lazy loader that loads blobs and parses them into documents.
        Blob by blob.

        When you're implementing lazy load methods, you should use a generator
        to yield documents one by one.
        """

        logger.info(f"Downloading files with blobLoader: {self.blobLoader} and parsing them with blobParser: {self.blobParser}")

        # Blob by blob
        for blob in self.blobLoader.yield_blobs():
            # extract text from downloaded file
            logger.info(f"Blob to parse: {blob}")

            # parse
            documents = list(self.blobParser.lazy_parse(blob))

            # result
            logger.info(f"Extracted documents yielded now: {documents}")
            yield from documents
