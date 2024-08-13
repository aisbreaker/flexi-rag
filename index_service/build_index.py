### Build Index

from hashlib import sha256
import os
from sqlite3 import Connection
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader #, FileBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import shortuuid
from index_service.wget_document_loader import WgetDocumentLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
)

from utils.string_util import str_limit

sqlCon: Connection | None = None
vectorStoreRetriever = None

#
# (Persitent) Data Model:
#
# The basic idea is to have documents (table 'document') and 
# # connected document parts (table 'document_part') in the SQL DB.
# These documents and their connected parts can change over time.
#
# And we have a parts (=text snippets + their sha256 hash + their embedding )
# which are stored/cached almost forever to save embedding-calculation costs and time.
# These parts are stored in the 'part' table in the SQL DB
# and in the vectorstore DB.
# Parts are identified and connected by their sha256 hash.
#
DB_TABLE_document = """CREATE TABLE IF NOT EXISTS document (
                            id TEXT NOT NULL PRIMARY KEY,
                            source TEXT NOT NULL,
                            content_type TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            file_size INTEGER NOT NULL,
                            file_sha256 TEXT NOT NULL,
                            last_modified TEXT NOT NULL
                    )"""
DB_TABLE_document_part = """CREATE TABLE IF NOT EXISTS document_part (
                                document_id TEXT NOT NULL,
                                part_sha256 TEXT NOT NULL,
                                anker TEXT COMMENT "position of the part in the document - e.g., page number, paragraph number, ..."
                            )"""

DB_TABLE_part = """CREATE TABLE IF NOT EXISTS part (
                       sha256 TEXT NOT NULL PRIMARY KEY COMMENT "sha256 hash of the content of this part, also used as ID in the vectorstore",
                       content TEXT NOT NULL
                   )"""




# in-memory queue of strings (filenames)
queue = []

"""
def crawl_single_url_with_wget(url):
    # crawl with wget with popen
    # and read name of downloaded files from stdin/stdout (with popen)
    import subprocess
    import os
    import io

    proc = subprocess.Popen(
        f"wget --directory-prefix /tmp/wget --recursive -l1 --no-parent -A.html,.txt,.mp4,.pdf --limit-rate=1024k --wait=3 {url}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        shell=True
    )
    for line in io.TextIOWrapper(proc.stderr, encoding="utf-8"):  # or another encoding
        # do something with line
        # trim the line
        print("    WGET: " + line.strip())
        # extract <filename> from line with "‘<filename>’ saved"
        if "‘" in line and "’ saved" in line:
            filename = line.split("‘")[1].split("’ saved")[0]
            print("WGET FILENAME: " + filename)
            # add filename to an in-memory queue
            queue.append(filename)
"""


    #for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
    #    # do something with line
    #    print("WGET: " + line)
    

# main function
def build_index_func():
    ### from langchain_cohere import CohereEmbeddings

    # Set embeddings
    embd = OpenAIEmbeddings()

    # Docs to index
    urls = [
        "https://dance123.org/",
        #"https://file-examples.com/storage/fe44eeb9cb66ab8ce934f14/2017/04/file_example_MP4_480_1_5MG.mp4",
    ]

    # crawl/load all documents from all URLs
    print(f"Loading WgetDocumentLoader from ... {urls}")
    docs = [WgetDocumentLoader(url).load() for url in urls]

    print(f"Flatten all loaded documents from ... {str_limit(docs, 1024)}")
    docs_list = [item for sublist in docs for item in sublist]
        # TODO: flatten in a reactive way, i.e., load and process documents one by one

    print("Save documents in SQL DB ...")
    docs_list_stored = save_docs_in_sqlite3_db(docs_list)

    #print("Documents...")
    #for doc in docs_list:
    #    print(f"doc={doc}")
    #    #print(f"Document: page_content: {doc.page_content}, metadata: {doc.metadata}")
    #    print(f"next doc={next(doc) if doc else None}")
    #
    #    for d in doc:
    #        print(f"Document: d: {d}")
    #        print(f"Document: page_content: {d.page_content}, metadata: {d.metadata}")  
    #print("Documents... done")



    print("==================================== 1")

    print(f"Splitting documents... {docs_list_stored}")

    # TODO: split (maybe slit doc by dock in a yield loop to remain reative)

        # save doc with all chunks in SQL DB

        # save all chunks in SQL DB

        # save all chunks in vectorstore

    create_index_db_from_docs_list(docs_list_stored, embd)
    print("==================================== 2")




def XXXbuild_index_func():
    ### from langchain_cohere import CohereEmbeddings

    # Set embeddings
    embd = OpenAIEmbeddings()

    # Docs to index
    urls = [
        "https://lilianweng.github.io/posts/2023-06-23-agent/",
        "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
        "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
    ]

    # Load
    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]

    create_index_db_from_docs_list(docs_list, embd)
    
def get_sqlite3_db_connection() -> Connection:
    import sqlite3
    SQL_DB_PATH = "./content.db"
    global sqlCon
    if sqlCon is None:
        sqlCon = sqlite3.connect(SQL_DB_PATH)
    return sqlCon

# iterate over the documents, save them in SQL DB, and add IDs
def save_docs_in_sqlite3_db(docs_list: Iterator[Document]) -> Iterator[Document]:
    print(f"save_docs_in_sqlite3_db ...")
    
    sqlCon = get_sqlite3_db_connection()
    #cur = sqlCon.cursor()

    # setup if necessary
    # - a document represents a a full file/document

    sqlCon.execute(DB_TABLE_document)

    # insert documents
    num = 0
    for doc in docs_list:
        print(f"save_docs_in_sqlite3_db: doc.metadata={str_limit(doc.metadata, 1024)} doc.page_content={str_limit(doc.page_content)}")

        # create uuid
        id = "doc-"+str(shortuuid.uuid()[:7])
        print(f"doc.metadata={doc.metadata}")
        source = doc.metadata['source']
        content_type = doc.metadata['content_type']
        file_path = doc.metadata['file_path']
        file_size = doc.metadata['file_size']
        file_sha256 = doc.metadata['file_sha256']
        last_modified = doc.metadata['last_modified']
        if False:
            # update row
            print("UPDATE documents SET url = ?, file_path = ?, content = ?, last_modified = ? WHERE id = ?", (doc.metadata.url, doc.page_content, doc.metadata))
        # else
        else:
            # inser row
            print(f"insert document row: id={id}, source={source}")
            num += 1
            sqlCon.execute(
                """INSERT INTO document (id, source, content_type, file_path, file_size, file_sha256, last_modified)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (id, source, content_type, file_path, file_size, file_sha256, last_modified)
            )
            sqlCon.commit()

        print_all_docs_from_sqlite3_db()

        doc.metadata["id"] = id
        doc.metadata["document_id"] = id
        yield doc
    
    # iteration done
    print(f"save_docs_in_sqlite3_db: {num} row(s) inserted - DONE")




# iterate over the document parts, save them in SQL DB, and add IDs
def save_doc_parts_in_sqlite3_db(doc_parts_list: Iterator[Document]) -> Iterator[Document]:
    print(f"save_doc_parts_in_sqlite3_db ...")

    sqlCon = get_sqlite3_db_connection()
    #cur = sqlCon.cursor()

    # setup if necessary
    # a document part represents a part of a document after splitting, e.g., a page, a paragraph, a part of a page
    sqlCon.execute(DB_TABLE_document_part)

    # insert document parts
    num = 0
    for doc_part in doc_parts_list:
        print(f"save_doc_parts_in_sqlite3_db: doc_part.metadata={str_limit(doc_part.metadata, 1024)} doc_part.page_content={str_limit(doc_part.page_content)}")

        # get document_id
        document_id = doc_part.metadata['document_id']

        # create part id = sha256 hash
        part_content = doc_part.page_content
        part_sha256 = sha256(part_content.encode()).hexdigest()

        # extract anker from metadata
        anker = None
        if "anker" in doc_part.metadata:
            anker = doc_part.metadata['anker']
        elif "page_number" in doc_part.metadata:
            anker = f"page {doc_part.metadata['page_number']}"
        elif "start_index" in doc_part.metadata:
            anker = doc_part.metadata['start_index']
        content = doc_part.page_content

        # insert OR NOT (TODO: check if part already exists)
        if False:
            # update row
            print("UPDATE documents SET url = ?, file_path = ?, content = ?, last_modified = ? WHERE id = ?", (doc.metadata.url, doc.page_content, doc.metadata))
        # else
        else:
            # insert row
            print(f"insert document_part row: id={id}, document_id={document_id}")
            """
                                document_id TEXT NOT NULL,
                                part_sha256 TEXT NOT NULL,
                                anker TEXT COMMENT "position of the part in the document - e.g., page number, paragraph number, ..."
            """

            num += 1
            sqlCon.execute(
                """INSERT INTO document_part (document_id, part_sha256, anker)
                                      VALUES (?, ?, ?)""",
                (document_id, part_sha256, anker)
            )
            sqlCon.commit()

        doc_part.metadata["id"] = id
        yield doc_part
    
    # iteration done
    print(f"save_doc_parts_in_sqlite3_db: {num} row(s) inserted - DONE")

def print_all_docs_from_sqlite3_db():
    sqlCon = get_sqlite3_db_connection()
    cur = sqlCon.cursor()
    cur.execute("SELECT * FROM document")
    rows = cur.fetchall()
    print(f"All Documents in SQL DB ({len(rows)} rows):")
    for row in rows:
        print("  DB row: "+str_limit(row, 200))
    print("All Documents in SQL DB - DONE")

def print_all_doc_parts_from_sqlite3_db():
    sqlCon = get_sqlite3_db_connection()
    cur = sqlCon.cursor()
    cur.execute("SELECT * FROM document_part")
    rows = cur.fetchall()
    print(f"All Document Parts in SQL DB ({len(rows)} rows):")
    for row in rows:
        print("  DB row: "+str_limit(row, 100))
    print("All Document Parts in SQL DB - DONE")

def process_single_document_and_store_results_in_databaes(doc: Document):
    # TODO

    # split doc into parts
    doc_splits = split_single_document_into_parts(doc)

    # process sha256 hashes of doc parts
    #TODO

    # save doc in SQL DB
    save_single_document_and_its_parts_in_sql_db(doc, doc_splits)

    # save doc parts in vectorstore
    save_parts_of_a_single_document_in_vectorstore(doc, doc_splits)

def save_single_document_and_its_parts_in_sql_db(doc: Document, doc_parts: Iterator[Document]):
    # save doc in SQL DB
    doc_stored = save_docs_in_sqlite3_db([doc])
    # save doc parts in SQL DB
    doc_parts_stored = save_doc_parts_in_sqlite3_db(doc_parts)
    return doc_stored, doc_parts_stored

def save_parts_of_a_single_document_in_vectorstore(doc: Document, doc_parts: Iterator[Document]):
    # TODO
    print("save_parts_of_a_single_document_in_vectorstore: TODO")


# TODO: use
def split_single_document_into_parts(doc: Document) -> List[Document]:
    # Split
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=50, chunk_overlap=10
    )
    doc_splits = text_splitter.split_documents([doc])
    return doc_splits


def split_documents_into_parts(docs: Iterator[Document]) -> Iterator[Document]:
    for doc in docs:
        yield from split_single_document_into_parts(doc)

def create_index_db_from_docs_list(docs_list: Iterator[Document], embd: Embeddings):
    global vectorStoreRetriever
    
    # Split
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=50, chunk_overlap=10
    )
    doc_splits = text_splitter.split_documents(docs_list)
    doc_splits2 = list(save_doc_parts_in_sqlite3_db(doc_splits))

    # Add to vectorstore
    CHROMA_DB_PATH = "./chroma_db"
    createNewDB = False #True
    # check if we need to create a new DB/if the directory exists
    if not os.path.exists(CHROMA_DB_PATH):
        createNewDB = True
    # create or load DB
    if createNewDB:
        vectorstore = Chroma.from_documents(
            documents=doc_splits2,
            collection_name="rag-chroma",
            embedding=embd,
            persist_directory=CHROMA_DB_PATH,
        )
    else:
        vectorstore = Chroma(
            collection_name="rag-chroma",
            embedding_function=embd,
            persist_directory=CHROMA_DB_PATH,
        )

    # the vector DB:
    vectorStoreRetriever = vectorstore.as_retriever()

    # print summary of Chroma vectorstore
    print("{} documents in vectorstore".format(len(vectorstore.get()['documents'])))


"""
def takeNextElementFromQueueAndIndex():
    if len(queue) > 0:
        filename = queue.pop(0)
        print("INDEXING: " + filename)
        # load the file
        FileBaseLoader(filename).load()
        # split the file
        # add to vectorstore

        # Add to vectorstore
        CHROMA_DB_PATH = "./chroma_db"
        createNewDB = False #True
        if createNewDB:
            vectorstore = Chroma.from_documents(
                documents=doc_splits,
                collection_name="rag-chroma",
                embedding=embd,
                persist_directory=CHROMA_DB_PATH,
            )
        else:
            vectorstore = Chroma(
                collection_name="rag-chroma",
                embedding_function=embd,
                persist_directory=CHROMA_DB_PATH,
            )



    else:
        print("Queue is empty - nothing to index at the moment")
"""
