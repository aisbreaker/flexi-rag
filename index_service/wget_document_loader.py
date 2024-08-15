import os
from typing import Iterator

from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
)

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_community.document_loaders.helpers import detect_file_encodings

import logging

from utils.hash_util import sha256sum
from utils.string_util import str_limit

logger = logging.getLogger(__name__)

class DownloadedFile:

    def __init__(
        self,
        url: str,
        file_path: str, # Union[str, List[str], Path, List[Path]],
        file_size: int,
        content_type: str | None,
    ):
        self.url = url
        self.file_path = file_path
        self.file_size = file_size
        self.content_type = content_type

    def __str__(self):
        return f"DownloadedFile(url={self.url}, file_path={self.file_path}, file_size={self.file_size}, content_type={self.content_type})"

    def __repr__(self):
        return str(self)

# TODO: remove:
#_MetadataExtractorType = Callable[[str, str], dict]
    #??? Add generic extractor logic?
    # extractor: Optional[Callable[[str], str]] = None,
    # metadata_extractor: Optional[_MetadataExtractorType] = None,

class WgetDocumentLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, url: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        self.url = url

    def lazy_load(self) -> Iterator[Document]:  # <-- Does not take any arguments
        """A lazy loader that reads a file line by line.

        When you're implementing lazy load methods, you should use a generator
        to yield documents one by one.
        """

        # crawl with wget and iterate over the downloaded files
        logger.info(f"Downloading files from url: {self.url}")
        for downloadedFile in WgetDocumentLoader.crawl_single_url_with_wget(self.url):
            # extract text from downloaded file
            logger.info(f"Downloaded file: {downloadedFile}")

            # extract metadata from downloaded file
            metadata = self.getDownloadedFileMatadata(downloadedFile)
            downloadedFile.content_type = metadata["content_type"]

            # extract content (document(s)) from downloaded file
            logger.info(f"Extracting content (document(s)) from downloaded file: {downloadedFile}")
            documents = list(self._generic_extractor(downloadedFile, metadata))
            logger.info(f"Extracted documents yielded now: {documents}")
            yield from documents
 

    @staticmethod
    def getDownloadedFileMatadata(downloadedFile: DownloadedFile) -> Dict[str, Any]:
        content_type = downloadedFile.content_type
        if content_type is None:
            urlLower = downloadedFile.url.lower()
            if urlLower.endswith(".html") or urlLower.endswith(".htm"):
                content_type = "text/html"
            elif urlLower.endswith(".xml"):
                content_type = "text/xml"
            elif urlLower.endswith(".pdf"):
                content_type = "application/pdf"
            else:
                content_type = "text/plain"
        file_sha256 = sha256sum(downloadedFile.file_path)
        logger.info(f"getDownloadedFileMatadata() metadata: {downloadedFile} -> content_type: {content_type}, file_sha256: {str_limit(file_sha256, 7)}...")
        return {
            "source": downloadedFile.url,
            "content_type": content_type,
            "file_path": downloadedFile.file_path,
            "last_modified": os.path.getmtime(downloadedFile.file_path),
            "file_size": downloadedFile.file_size,
            "file_sha256": file_sha256 
        }

    @staticmethod
    def _generic_extractor(downloaded: DownloadedFile, metadata: Dict[str, Any]) -> Iterator[Document]:
        if downloaded.content_type == "text/plain":
            return WgetDocumentLoader._text_extractor(downloaded, metadata)
        elif downloaded.content_type == "text/html" or downloaded.content_type == "text/xml":
            return WgetDocumentLoader._html_xml_extractor(downloaded, metadata)
        elif downloaded.content_type == "application/pdf":
            return WgetDocumentLoader._pdf_extractor(downloaded, metadata)
        else:
            # default: (plain) text extractor
            return WgetDocumentLoader._text_extractor(downloaded, metadata)

    @staticmethod
    def _pdf_extractor(downloaded: DownloadedFile, metadata: Dict[str, Any]) -> Iterator[Document]:
        """Extract text from a PDF file."""
        from langchain_community.document_loaders import PyPDFLoader

        # TODO XXXXXXXXXXXXXXXXXXX
        loader = PyPDFLoader(downloaded.file_path)
        pages = loader.load_and_split() #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
        for page_number, page_text in enumerate(pages):
            yield Document(
                page_content=page_text,
                metadata={"page_number": page_number, "source": downloaded.url},
            )

            # PDF extrator
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader("example_data/layout-parser-paper.pdf")
            pages = loader.load_and_split()
            pages.__iter__()



    @staticmethod
    def _text_extractor(downloaded: DownloadedFile, metadata: Dict[str, Any]) -> Iterator[Document]:
        """Extract text from a plain text."""

        # read file content
        try:
            logger.info(f"Extracting A plain text from downloaded file: {downloaded}")
            file_content = WgetDocumentLoader._load_text_file(downloaded.file_path).strip()
            yield Document(
                page_content = file_content,
                metadata = metadata
            )
            return
        except Exception as e:
            logger.info(f"ERROR: Extractor error for: {downloaded.content_type} and url: {downloaded.url}  - {e}")
            # empty result:
            yield from () # explanation: https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/13243870#13243870
            return

    @staticmethod
    def _html_xml_extractor(downloaded: DownloadedFile, metadata: Dict[str, Any]) -> Iterator[Document]:
        """Extract text from a HTML or XML file."""

        # select HTML/XML parser for BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser)
        if downloaded.content_type == "text/xml":
            # XML
            bs_parser = "xml"
        else:
            # default: HTML
            bs_parser = "html.parser"

        # read file content and pass to BeautifulSoup
        try:
            logger.info(f"Extracting A text from downloaded file: {downloaded} with bs_parser: {bs_parser}")
            from bs4 import BeautifulSoup
            file_content = WgetDocumentLoader._load_text_file(downloaded.file_path)
            if file_content:
                logger.info(f"Extracting B text from downloaded file: {downloaded} with file_content: '{str_limit(file_content)}'")

                # parse with HTML or XML with BeautifulSoup
                logger.info(f"Extracting text from downloaded file with BeautifulSoup: {downloaded}")
                WgetDocumentLoader._check_bs_parser(bs_parser)
                bs_kwargs: Optional[Dict[str, Any]] = None
                bs_get_text_kwargs: Optional[Dict[str, Any]] = None
                bs = BeautifulSoup(file_content, bs_parser, **(bs_kwargs or {}))
                logger.info(f"Extracting text from downloaded file with BeautifulSoup done: {downloaded}")
                try:
                    # extract text from bs4 object
                    text = bs.get_text(**(bs_get_text_kwargs or {})).strip()
                    logger.info(f"Extracted text from downloaded file with BeautifulSoup: {downloaded} -> '{str_limit(text)}'")
                    yield Document(
                        page_content = text,
                        metadata = metadata
                    )
                    return
                except Exception as e:
                    logger.info(f"ERROR: Extractor error for content_type: {downloaded.content_type} and url: {downloaded.url} and bs_parser: {bs_parser} - {e}")
                    # empty result:
                    yield from ()
                return
            
            else:
                logger.info(f"ERROR: Extractor error for content_type: {downloaded.content_type} and url: {downloaded.url} and bs_parser: {bs_parser} - no file content")
                # empty result:
                yield from () # explanation: https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/13243870#13243870
                return

        except Exception as e:
            logger.info(f"ERROR: Extractor error for content_type: {downloaded.content_type} and url: {downloaded.url} and bs_parser: {bs_parser} - {e}")
            # empty result:
            yield from () # explanation: https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/13243870#13243870
            return

    @staticmethod
    def _load_text_file(file_path: str) -> Optional[str]:
        default_encoding: Optional[str] = "utf-8"

        text: Optional[str] = None
        try:
            logger.info(f"_load_text_file: {file_path}")
            with open(file_path, "r", encoding=default_encoding) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            logger.info(f"_load_text_file E1: {file_path}")

            detected_encodings = detect_file_encodings(file_path)
            for default_encoding in detected_encodings:
                logger.debug(f"_load_text_file: Trying encoding: {default_encoding.encoding}")
                try:
                    with open(file_path, encoding=default_encoding.encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            raise RuntimeError(f"Error loading {file_path}") from e
            logger.warning(f"_load_text_file: Error B loading {file_path}: {e}")
            logger.info(f"_load_text_file: ERROR: Error B loading {file_path}: {e}")
            return None
        
        return text


    @staticmethod
    def _check_bs_parser(parser: str) -> None:
        """Check that parser is valid for bs4."""
        valid_parsers = ["html.parser", "lxml", "xml", "lxml-xml", "html5lib"]
        if parser not in valid_parsers:
            raise ValueError(
                "`parser` must be one of " + ", ".join(valid_parsers) + "."
            )

    @staticmethod
    def crawl_single_url_with_wget(url) -> Iterator[DownloadedFile]:
        # crawl with wget with popen
        # and read name of downloaded files from stdin/stdout (with popen)
        import subprocess
        import os
        import io

        directory_prefix = "/tmp/wget"
        proc = subprocess.Popen(
            f"wget --directory-prefix {directory_prefix} --recursive -l1 --no-parent -A.html,.txt,.mp4,.pdf --limit-rate=1024k --wait=10 {url}",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            shell=True
        )
        for line in io.TextIOWrapper(proc.stderr, encoding="utf-8"):  # or another encoding
            # do something with line
            # trim the line
            logger.info("    WGET: " + line.strip())
            # extract <file_path> from line with "‘<file_path>’ saved"
            if "‘" in line and "’ saved" in line:
                # extract file_path from line
                file_path = line.split("‘")[1].split("’ saved")[0]
                # derive url from file_path
                if file_path.startswith(directory_prefix):
                    dir_prefix2 = directory_prefix
                    if not file_path.endswith("/"):
                        dir_prefix2 = directory_prefix + "/"
                    file_path_without_prefix = file_path[len(dir_prefix2):]
                    url = "https://" + file_path_without_prefix
                else:
                    url = "file://" + file_path
                
                #content_type = "text/html" # TODO: extract form wget output "Length: 2588 (2,5K) [text/html]"
                content_type = None
                file_size = os.path.getsize(file_path) # OR: # TODO: extract form wget output "Length: 2588 (2,5K) [text/html]"
                logger.info(f"WGET downloaded url: {url} -> file_path: {file_path} (content_type: {content_type}, file_length: {file_size})")
                downloadedFile = DownloadedFile(url, file_path, file_size, content_type)
                yield downloadedFile
