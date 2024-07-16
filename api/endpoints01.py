from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.orchestration import initialize_workflow, execute_workflow

router = APIRouter()

class ChatRequest(BaseModel):
    model: str
    messages: list

class EmbeddingsRequest(BaseModel):
    input: list
    model: str

@router.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        config = {}  # Load your LangGraph config here
        lg = initialize_workflow(config)
        response = execute_workflow(lg, request.messages)
        return {"choices": [{"text": response}]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/embeddings")
async def embeddings(request: EmbeddingsRequest):
    try:
        # Implement your embedding generation logic here
        embeddings = generate_embeddings(request.input, request.model)
        return {"data": embeddings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_embeddings(inputs, model):
    # Logic for generating embeddings using the specified model
    embeddings = []
    for input in inputs:
        # Call the appropriate API to generate embeddings
        embedding = call_embedding_api(input, model)
        embeddings.append(embedding)
    return embeddings

def call_embedding_api(input, model):
    # Example function to call an external embedding API
    return {"object": "embedding", "embedding": [0.1, 0.2, 0.3], "index": 0}

