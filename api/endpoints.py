# langserve doesn’t have a built-in function for OpenAI compatibility
# create custom endpoints manually:

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
#from workflow.workflow import create_workflow
from workflow.simple_workflow import create_workflow
from langchain_core.chat_history import BaseChatMessageHistory

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
    """
    Example request:
    {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": The Los Angeles Dodgers won the World Series in 2020. Where was it played?"
            }
        ]
    }

    Example response (Non-Streaming):
    {
        "choices": [
            {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": "The 2020 World Series was played in Texas at Globe Life Field in Arlington.",
                "role": "assistant"
            },
            "logprobs": null
            }
        ],
        "created": 1677664795,
        "id": "chatcmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW",
        "model": "gpt-4o-mini",
        "object": "chat.completion",
        "usage": {
            "completion_tokens": 17,
            "prompt_tokens": 57,
            "total_tokens": 74
        }
    }
    """

    try:
        result = workflow.invoke({"messages": request.messages})  # Adjust according to your workflow execution method
        return {
            "choices": [{
                "message": {
                    "content": result['generation'].content,
                    "role": "assistant"
                }
            }]
        }
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
