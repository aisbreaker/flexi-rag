import logging
from service.configloader import settings, deep_get
from service.logging_setup import setup_logging

logger = logging.getLogger(__name__)

# setup
setup_logging()

# test settings
#llms=deep_get(settings, 'config.common.llms')
#logger.info(f"config.common.llms={llms}")
#oai=deep_get(llms, 'ChatOpenAI_default_llm')
#logger.info(f"oai={oai}")
#oai_module=deep_get(llms, 'ChatOpenAI_default_llm.module')
#logger.info(f"oai_module={oai_module}")
#invalid_module=deep_get(settings, 'config.common.llms.invalid.foo') #, None)
#logger.info(f"invalid_module={invalid_module}")


# standalone command execution




# start building the index
from rag_index_service import build_index
build_index.start_indexing()


# start server with API
if True:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from exported_api import endpoints
    from exported_api import admin_endpoints

    app = FastAPI()

    @app.get("/hello")
    def get_hello():
        return {"message": "Welcome to the AI RAG API"}

    @app.get("/health")
    # https://stackoverflow.com/questions/46949108/spec-for-http-health-checks/47119512#47119512
    def get_health():
        return {"status": "healthy"}

    # /api/*
    app.include_router(endpoints.router)

    # /admin/*
    app.include_router(admin_endpoints.router)

    # /* for static files - the request are processed IN THE ORDER the mounts are defined here
    app.mount("/chat", StaticFiles(directory="static_chat",html = True))
    app.mount("/", StaticFiles(directory="static",html = True))

    # run the HTTP server
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
