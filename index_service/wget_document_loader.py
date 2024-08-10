from hashlib import sha256
import os
from typing import AsyncIterator, Iterator

from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Union,
)

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_community.document_loaders.helpers import detect_file_encodings

import logging

from utils.string_util import str_limit

logger = logging.getLogger(__name__)

class DownloadedFile:

    def __init__(
        self,
        url: str,
        file_path: str, # Union[str, List[str], Path, List[Path]],
        file_length: int,
        content_type: str,
    ):
        self.url = url
        self.file_path = file_path
        self.file_length = file_length
        self.content_type = content_type

    def __str__(self):
        return f"DownloadedFile(url={self.url}, file_path={self.file_path}, file_length={self.file_length}, content_type={self.content_type})"

    def __repr__(self):
        return str(self)

_MetadataExtractorType = Callable[[str, str], dict]

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
        print(f"Downloading files from url: {self.url}")
        for downloadedFile in self.crawl_single_url_with_wget(self.url):
            # extract text from downloaded file
            print(f"Downloaded file: {downloadedFile}")

            # PDF? TODO


            # HTML/XML/plain text?
            print(f"Extracting text from downloaded file: {downloadedFile}")
            result = self._text_html_xml_extractor(downloadedFile)
            print(f"Extracted text: {result}")
            # dodn't iterate over the result, because it would consume/empty the generator - just yield it
            #for r in result:
            #    print(f"Extracted text: Yielded: {r}")
            print(f"Extracted text: Yielded now")
            yield from result
 

            """
            content = self.extractor(response.text)
            if content:
                yield Document(
                    page_content=content,
                    metadata=self.metadata_extractor(response.text, url, response),
                )


            with open(downloadedFile.file_path, encoding="utf-8") as f:
                line_number = 0
                for line in f:
                    yield Document(
                        page_content=line,
                        metadata={"line_number": line_number, "source": self.url},
                    )
                    line_number += 1 
            """

    @staticmethod
    def _pdf_extractor(downloaded: DownloadedFile) -> Iterator[Document]:
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

    # extractor: Optional[Callable[[str], str]] = None,
    # metadata_extractor: Optional[_MetadataExtractorType] = None,
    @staticmethod
    def _text_html_xml_extractor(downloaded: DownloadedFile) -> Iterator[Document]:
        """Extract text from a plain text or HTML or XML file."""

        from bs4 import BeautifulSoup

        # select HTML/XML parser for BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser)
        default_bs_parser = "html.parser"
        bs_parser = default_bs_parser
        urlLower = downloaded.url.lower()
        if bs_parser is None and downloaded.content_type == "text/xml":
            bs_parser = "xml"
        elif downloaded.content_type == "text/html":
            bs_parser = "html.parser"
        elif urlLower.endswith(".html") or urlLower.endswith(".htm"):
            bs_parser = "html.parser"
            downloaded.content_type == "text/html"
        elif downloaded.url.endswith(".xml"):
            bs_parser = "xml"
            downloaded.content_type == "text/xml"
        else:
            # fallback to plain text
            bs_parser = None
            downloaded.content_type == "text/plain"

        # read file content and pass to BeautifulSoup
        try:
            print(f"Extracting A text from downloaded file: {downloaded} with bs_parser: {bs_parser}")
            file_content = WgetDocumentLoader._load_text_file(downloaded.file_path)
            if file_content:
                print(f"Extracting B text from downloaded file: {downloaded} with file_content: '{str_limit(file_content)}'")
                # default? Text! -> nothing to parse
                if bs_parser is None:
                    # use plain text
                    print(f"Extracting plain text from downloaded file: {downloaded}")
                    last_modified = os.path.getmtime(downloaded.file_path)
                    yield Document(
                        page_content=file_content,
                        metadata={
                            "source": downloaded.url,
                            "content_type": downloaded.content_type,
                            "file_path": downloaded.file_path,
                            "last_modified": last_modified,
                            "size": downloaded.file_length,
                            "file_size": downloaded.file_length
                        },
                    )
                    return

                # parse with HTML or XML with BeautifulSoup
                print(f"Extracting text from downloaded file with BeautifulSoup: {downloaded}")
                WgetDocumentLoader._check_bs_parser(bs_parser)
                bs_kwargs: Optional[Dict[str, Any]] = None
                bs_get_text_kwargs: Optional[Dict[str, Any]] = None
                bs = BeautifulSoup(file_content, bs_parser, **(bs_kwargs or {}))
                print(f"Extracting text from downloaded file with BeautifulSoup done: {downloaded}")
                try:
                    # extract text from bs4 object
                    text = bs.get_text(**(bs_get_text_kwargs or {}))
                    print(f"Extracted text from downloaded file with BeautifulSoup: {downloaded} -> '{str_limit(text)}'")
                    last_modified = os.path.getmtime(downloaded.file_path)
                    content_sha256 = sha256(file_content.encode('utf-8')).hexdigest()
                    yield Document(
                        page_content=text,
                        metadata={
                            "source": downloaded.url,
                            "content_type": downloaded.content_type,
                            "content_sha256": content_sha256,
                            "file_path": downloaded.file_path,
                            "last_modified": last_modified,
                            "size": downloaded.file_length,
                            "file_size": downloaded.file_length
                        },
                    )
                    return
                except Exception as e:
                    print(f"ERROR: Extractor error for content_type: {downloaded.content_type} and url: {downloaded.url} and bs_parser: {bs_parser} - {e}")
                    # empty result:
                    yield from ()
                return
            
            else:
                print(f"ERROR: Extractor error for content_type: {downloaded.content_type} and url: {downloaded.url} and bs_parser: {bs_parser} - no file content")
                # empty result:
                yield from () # explanation: https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/13243870#13243870
                return

        except Exception as e:
            print(f"ERROR: Extractor error for content_type: {downloaded.content_type} and url: {downloaded.url} and bs_parser: {bs_parser} - {e}")
            # empty result:
            yield from () # explanation: https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/13243870#13243870
            return

    @staticmethod
    def _load_text_file(file_path: str) -> Optional[str]:
        encoding: Optional[str] = "utf-8"
        autodetect_encoding: bool = True

        text: Optional[str] = None

        try:
            print(f"_load_text_file: {file_path}")
            with open(file_path, "r", encoding=encoding) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            print(f"_load_text_file E1: {file_path}")
            if autodetect_encoding:
                detected_encodings = detect_file_encodings(file_path)
                for encoding in detected_encodings:
                    logger.debug(f"_load_text_file: Trying encoding: {encoding.encoding}")
                    try:
                        with open(file_path, encoding=encoding.encoding) as f:
                            text = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {file_path}") from e
                logger.warning(f"_load_text_file: Error A loading {file_path}: {e}")
                print(f"_load_text_file: ERROR: Error A loading {file_path}: {e}")
                return None
        except Exception as e:
            raise RuntimeError(f"Error loading {file_path}") from e
            logger.warning(f"_load_text_file: Error B loading {file_path}: {e}")
            print(f"_load_text_file: ERROR: Error B loading {file_path}: {e}")
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

    def crawl_single_url_with_wget(self, url) -> Iterator[DownloadedFile]:
        # crawl with wget with popen
        # and read name of downloaded files from stdin/stdout (with popen)
        import subprocess
        import os
        import io

        directory_prefix = "/tmp/wget"
        proc = subprocess.Popen(
            f"wget --directory-prefix {directory_prefix} --recursive -l1 --no-parent -A.html,.txt,.mp4,.pdf --limit-rate=1024k --wait=3 {url}",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            shell=True
        )
        for line in io.TextIOWrapper(proc.stderr, encoding="utf-8"):  # or another encoding
            # do something with line
            # trim the line
            print("    WGET: " + line.strip())
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
                
                content_type = "text/html" # TODO: extract form wget output "Length: 2588 (2,5K) [text/html]"
                file_length = os.path.getsize(file_path) # OR: # TODO: extract form wget output "Length: 2588 (2,5K) [text/html]"
                print(f"WGET downloaded url: {url} -> file_path: {file_path} (content_type: {content_type}, file_length: {file_length})")
                downloadedFile = DownloadedFile(url, file_path, file_length, content_type)
                yield downloadedFile
