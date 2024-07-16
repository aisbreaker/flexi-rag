

# standalone command execution

# call build_index_py here
from index_service.build_index import retriever
print("== retriever")
print(retriever)

print ("-----")

from answer_service.generate_2 import generation
print("== generation")
print(generation)

# start server with API?
if False:
    from fastapi import FastAPI
    from app.api import endpoints

    app = FastAPI()

    app.include_router(endpoints.router)

    @app.get("/")
    def read_root():
        return {"message": "Welcome to the AI RAG API"}

    # You can add more initializations here if necessary

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)

