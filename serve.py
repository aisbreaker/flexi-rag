import langserve
import workflow.workflow as workflow


### LLMs
import os

os.environ["OPENAI_API_KEY"] = ""
os.environ["COHERE_API_KEY"] = ""
os.environ["TAVILY_API_KEY"] = ""

### Tracing (optional, https://docs.smith.langchain.com/)
#os.environ["LANGCHAIN_TRACING_V2"] = "true"
#os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
#os.environ["LANGCHAIN_API_KEY"] = ""




workflow = workflow.create_workflow()

# Create an OpenAI-compatible router
router = langserve.create_openai_compatible_router(workflow)

# Start the server with the router
langserve.serve(router, host="0.0.0.0", port=8000)
