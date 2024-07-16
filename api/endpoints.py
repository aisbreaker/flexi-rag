# langserve doesn’t have a built-in function for OpenAI compatibility
# create custom endpoints manually:

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from workflow.workflow import create_workflow

router = APIRouter()
workflow = create_workflow()

class ChatRequest(BaseModel):
    model: str
    messages: list

class EmbeddingsRequest(BaseModel):
    input: list
    model: str

@router.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        response = workflow.run(request.messages)  # Adjust according to your workflow execution method
        return {"choices": [{"text": response}]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/embeddings")
async def embeddings(request: EmbeddingsRequest):
    try:
        embeddings = generate_embeddings(request.input, request.model)
        return {"data": embeddings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_embeddings(inputs, model):
    # Logic for generating embeddings using the specified model
    embeddings = []
    for input in inputs:
        embedding = call_embedding_api(input, model)
        embeddings.append(embedding)
    return embeddings

def call_embedding_api(input, model):
    # Example function to call an external embedding API
    return {"object": "embedding", "embedding": [0.1, 0.2, 0.3], "index": 0}
