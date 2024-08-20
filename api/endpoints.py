# langserve doesn’t have a built-in function for OpenAI compatibility
# create custom endpoints manually:

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
#from workflow.workflow import create_workflow
from workflow.simple_workflow import create_workflow
from langchain_core.chat_history import BaseChatMessageHistory



logger = logging.getLogger(__name__)

router = APIRouter()
workflow = create_workflow()

class ChatRequest(BaseModel):
    model: str
    stream: Optional[bool] = False
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
        stream = request.stream
        """
        if not streaming:
            # non-streaming mode
            async def generate():
                result = workflow.invoke({"messages": request.messages})  # Adjust according to your workflow execution method
                yield {
                    "choices": [{
                        "message": {
                            "content": result['generation'].content,
                            "role": "assistant"
                        }
                    }]
                }

            return StreamingResponse(generate())
        else:
        """
        # steaming mode
        inputs = {"messages": request.messages, "stream_generate_on_last_node": stream}
        logger.info("Chunks: ") #, end="")
        async for event in workflow.astream_events(inputs, version="v2"):
            kind = event["event"]
            tags = event.get("tags", [])
            #logger.info("event="+kind+", tags="+str(tags)+", data="+str(event.get("data", {})))
            if kind == "on_chat_model_stream" or "final_node" in tags:
                #logger.info("event="+str(event))
                if kind == "on_chat_model_stream" and "final_node" in tags:
                    data = event["data"]
                    if data["chunk"].content:
                        # Empty content in the context of OpenAI or Anthropic usually means
                        # that the model is asking for a tool to be invoked.
                        # So we only print non-empty content
                        logger.info(data["chunk"].content) #, end="|")

        logger.info("[END Chunks]")

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
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
