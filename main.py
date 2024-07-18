

# standalone command execution

# call build_index_py here
#from index_service.build_index import vectorStoreRetriever
#import index_service
import index_service.build_index
index_service.build_index.build_index_func()

print("== retriever")
print(index_service.build_index.vectorStoreRetriever)

print ("-----")



print("== generation")
# call generate_2_py here
import answer_service.generate_2
question = "What is agent memory"
#question = "What is Java?"
answer = answer_service.generate_2.generate_answer(question)
print("answer:"+str(answer))

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

