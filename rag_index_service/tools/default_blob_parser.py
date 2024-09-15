from typing import Iterator, Mapping
from langchain_core.documents import Document
from langchain_core.documents.base import Blob
from langchain_community.document_loaders.base import BaseBlobParser
from langchain_community.document_loaders.parsers.generic import MimeTypeBasedParser
from langchain_community.document_loaders.parsers.html import BS4HTMLParser
from langchain_community.document_loaders.parsers.txt import TextParser
from langchain_community.document_loaders.parsers.pdf import PyPDFParser

class DefaultBlobParser(MimeTypeBasedParser):
    def __init__(self):
        # Define the parsers for the different mime types
        handlers: Mapping[str, BaseBlobParser] = {
            "text/html": BS4HTMLParser(),
            "text/plain": TextParser(),
            "application/pdf": PyPDFParser(),
        },
        fallback_parser = TextParser()
    
        # Call the parent class constructor
        super().__init__(handlers=handlers, fallback_parser=fallback_parser)


    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Load documents from a blob."""

        # Actual parsing
        result = super().lazy_parse(blob)

        # Post-processing
        for document in result:
            # Copy metadata from the blob to the document:
            # Iterate over the metadata of the blob
            for key, value in blob.metadata.items():
                # copy the metadata to the document, if it is not already present
                if key not in document.metadata:
                    document.metadata[key] = value

            # Result document
            yield document
