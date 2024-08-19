FlexiRAG
========

TMP
---

curl "http://localhost:8080/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Write a haiku that explains the concept of recursion."
            }
        ]
    }'


Steaming result from the final LangGraph node:
* HOWTO: https://langchain-ai.github.io/langgraph/how-tos/streaming-from-final-node/


Introduction
------------

The goal of this open-source project is to provide a single Docker image that implements AI RAG (Retrieval-Augmented Generation) in a highly configurable way.

Key facts:
- Implemented in Python with LangGraph.
- Fully configurable through a single YAML file, with useful defaults.
- Supports multiple alternative APIs (external services) for creating embeddings.
- Supports multiple alternative APIs (external services) for LLMs (Language Model Models).
- Supports multiple methods for retrieving data to populate the index database, including website crawling, Google Drive, S3, and local files within a specific folder.
- The index database can be either memory+file-based or an external service accessible via an API.


Status
------
This project is in a very early stage of development, not even ready for experimental use yet.

The algorithme use here is based on the Langchain example "Self-RAG". 
Self-RAG is a strategy for RAG that incorporates self-reflection / self-grading on retrieved documents and generations.

Code example:
- https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_self_rag.ipynb
- https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_self_rag/


Development / Usage
-------------------

Python run:

    python3 main.py


Python check:

    # installation of flake8 (hhttps://flake8.pycqa.org/en/latest/)
    python3 -m pip install flake8
    
    
    # full check
    python3 -m flake8 .
    
    
    # check for errors only
    python3 -m flake8 . | grep " F"


poetry?
-------

Ie we want to use poetry (and `pyproject.toml`) instaed of pip (and `requirements.txt`) in the future, then:

    poetry install

Read more: https://medium.com/@utkarshshukla.author/managing-python-dependencies-the-battle-between-pip-and-poetry-d12e58c9c168

