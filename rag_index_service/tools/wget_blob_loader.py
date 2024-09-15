import os
from typing import Any, Dict, Iterable, Iterator, Optional
#from langchain_community.document_loaders.blob_loaders.file_system import FileSystemBlobLoader
#from langchain_community.document_loaders.[blob_loaders.schema] import BlobLoader
from langchain_community.document_loaders import BlobLoader
from langchain_core.documents.base import Blob as Blob
from langchain_community.document_loaders.helpers import detect_file_encodings

import logging

from utils.hash_util import sha256sum
from utils.string_util import str_limit

logger = logging.getLogger(__name__)


class WgetBlobLoader(BlobLoader):
    def __init__(self, url: str):

        self.url = url

    def yield_blobs(
        self,
    ) -> Iterable[Blob]:
        """Yield blobs that match the requested pattern."""
        
        # crawl with wget and iterate over the blobs (downloaded files)
        logger.info(f"Downloading files from url: {self.url}")
        for blob in self.crawl_single_url_with_wget(self.url):
            # extract text from downloaded blob
            logger.info(f"Downloaded file: {blob}")
            yield blob


    @staticmethod
    def crawl_single_url_with_wget(url) -> Iterator[Blob]:
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
                
                # Construct result Blob
                blob_metadata: Dict[str, Any] = {
                    "source": url,
                    "file_size": file_size,
                    #"file_path": file_path,
                    #"content_type": content_type,
                }
                blob = Blob.from_path(
                    path = file_path,
                    encoding = WgetBlobLoader._guess_file_encoding(file_path),
                    mime_type = content_type,
                    guess_type = True,
                    metadata = blob_metadata,
                )
                blob = WgetBlobLoader._enrich_blob_metadata(blob)
                yield blob

    @staticmethod
    def _enrich_blob_metadata(blob: Blob) -> Dict[str, Any]:
        metadata: Dict[str, Any] = blob.metadata
        file_path = blob.path

        # Add content type
        if metadata.get("content_type") is None:
            metadata["content_type"] = blob.mimetype
        # Add file path
        if metadata.get("file_path") is None:
            metadata["file_path"] = file_path
        # Add file size
        if metadata.get("file_size") is None:
            metadata["file_size"] = os.path.getsize(file_path)
        # Add hash
        if metadata.get("file_sha256") is None:
            metadata["file_sha256"] = sha256sum(file_path)
        # Add last modified
        if metadata.get("last_modified") is None:
            metadata["last_modified"] = os.path.getmtime(file_path)

        # result
        #blob.metadata = metadata  # assignment not needed!
        return blob


    @staticmethod
    def _guess_file_encoding(file_path: str) -> Optional[str]:
        detected_encodings = detect_file_encodings(file_path)
        if len(detected_encodings) > 0:
            # the most likely encoding is the first one
            return detected_encodings[0].encoding
        
        # Fallback to utf-8
        default_encoding = "utf-8"
        return default_encoding


    # Probably not needed anymore:
    """
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
    """
