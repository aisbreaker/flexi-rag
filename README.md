# Flexi-RAG

## Introduction

[Flexi-RAG](https://github.com/aisbreaker/flexi-rag/) is an open-source project that provides a flexible, configurable AI solution for [Retrieval-Augmented Generation (RAG)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation) within a single container. It crawls specified external document sources, such as websites or S3 folders, indexes them, and offers an OpenAI-compatible API endpoint for data search and retrieval. This makes it compatible with any OpenAI-based chat interface.

### Key Features:
- **Single-container deployment**: Easily run in Docker or Kubernetes environments.
- **Simple configuration**: Set up with just one YAML file, plus optional environment variables.
- **Minimal setup**: Requires only an external LLM (e.g., OpenAI Chat API or equivalent).
- **Customizable document sources**: Define crawling targets in the YAML file.
- **Flexible integration**: Optionally configure LLMs, databases, and alternative RAG algorithms in the YAML file.
- **OpenAI-compatible REST API**: Retrieval results are accessible via an exposed API endpoint.
- **Included chat client**: A basic, OpenAI-compatible web chat client is provided for convenience.


## Get Involved

We welcome contributions from both developers and users! Whether you're looking to **enhance Flexi-RAG's capabilities**, integrate new features, improve documentation, **or simply share your experience and feedback**, your involvement is highly valued. As an open-source project, Flexi-RAG thrives on community collaboration. Developers can contribute by submitting pull requests, reporting issues, or suggesting new ideas. Users are encouraged to share use cases, request features, and help improve the project by providing insights from real-world applications. Together, we can make Flexi-RAG even more powerful and versatile. [Contact](https://aisbreaker.org/contact) us!


## Status

This project is currently in the early stages of development and is intended for development and experimental use only. At this time, no public Docker images are available. To get started, you'll need to clone the source code from the repository and build the container locally.


## Technical Details

Key technical aspects of the project:
- **Built with Python**: Utilizes LangChain and LangGraph frameworks for seamless integration and customization.
- **Flexible configuration**: The entire system is configurable via a single YAML file with sensible defaults, allowing for easy setup and customization.
- **Customizable algorithms**: Indexing and retrieval algorithms offer significant flexibility, allowing for fine-tuned configurations.
- **Embedding model support**: Any external embedding model supported by LangChain can be used, including all OpenAI API-compatible embedding services.
- **LLM compatibility**: You can use any external chat LLM supported by LangChain, including all OpenAI API-compatible chat completion services.
- **Vector store integration**: Supports all vector store databases available in LangChain, such as internal ChromaDB (in-memory or file-based) and external vector databases.
- **SQL database support**: Compatible with any SQL database that follows the Python DB-API 2.0 standard, including internal SQLite (in-memory or file-based) and external SQL databases.
- **Diverse document sources**: Supports multiple methods for document retrieval to populate the index, such as website crawling, Google Drive, S3, and local file directories.

By default, the project employs a simplified version of the LangChain "Self-RAG" approach for indexing and retrieval ([LangGraph Self-RAG Code](https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_self_rag.ipynb), [LangGraph Self-RAG Docs](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_self_rag/)).


## TODOs

Current tasks:
- Build the Docker image for deployment
- Test and verify the functionality of the Docker image
- Further refine and stabilize core features


## Future Enhancements

Potential future improvements:
- Implement a customizable workflow for building the index
- Factor out generic endspoints-logic that provides OpenAI-compatible API for a LangGraph workflow


## Development / Usage

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

