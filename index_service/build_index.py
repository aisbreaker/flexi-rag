### Build Index

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


#vectorStoreRetriever = None

def build_index_func():
    ### from langchain_cohere import CohereEmbeddings
    global vectorStoreRetriever

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

    # Split
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)

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

    # the vector DB:
    vectorStoreRetriever = vectorstore.as_retriever()

    # print summary of Chroma vectorstore
    print("{} documents in vectorstore".format(len(vectorstore.get()['documents'])))
