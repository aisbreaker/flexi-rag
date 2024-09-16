Flexi-RAG
=========

Introduction
------------

The goal of this open-source project is to provide a single Docker image that implements AI RAG (Retrieval-Augmented Generation) in a highly configurable way.

Key facts:
- Implemented in Python with LangChain/LangGraph.
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




TODOs
-----
... for now:
* improve docs and README
* build Docker image
* test Docker image


MAYBE LATER
-----------
TODOs for later:
* build-Index: with a configurable workflow?
* factors out generic endspoints-logic to provide OpenAI-compatible API




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


Development and Testing
-----------------------

Here we collect code snippets useful for developer tests ...


wget -r -l1 --include-directories=/dir1,/aisbroker/flexi-rag/ https://github.com/aisbroker/flexi-rag/tree/main/test-data


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

 # non-streaming
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
                "content": "Write 4 sentences about the concept of recursion."
            }
        ]
    }'

 # streaming
 #curl "https://api.openai.com/v1/chat/completions" \
curl "http://localhost:8080/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o-mini",
        "stream": true,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Write 2 sentences about the concept of recursion."
            }
        ]
    }'


curl "http://localhost:8080/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o-mini",
        "stream": true,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Write 2 sentences about Universal Adversarial Triggers."
            }
        ]
    }'

curl "http://localhost:8080/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o-mini",
        "stream": false,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Write 2 sentences about example domain."
            }
        ]
    }'

"Write 2 sentences about dance123."
"Write 2 sentences about Artificial Scalability."
"What are the types of agent memory?"

