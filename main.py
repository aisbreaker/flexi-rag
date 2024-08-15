import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(filename)s:%(funcName)s() - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# Set different levels for different modules
logging.getLogger('index_service').setLevel(logging.DEBUG)
logging.getLogger('answer_service').setLevel(logging.DEBUG)
#logging.getLogger('answer_service').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# standalone command execution

# call build_index_py here
#from index_service.build_index import vectorStoreRetriever
#import index_service
import index_service.build_index


index_service.build_index.start_indexing()
logger.info("fist indexing done XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")



print("== generation")
# call generate_2_py here
import answer_service.generate_2
question1 = "What is dance123?"
question2 = "What is short-term memory?" # no working well: "What is agent memory?"
#question2 = "What is Java?"

logger.info("=====================")
answer1 = answer_service.generate_2.generate_answer(question1)
logger.info("question1: "+str(question1))
logger.info("answer1:" +str(answer1))

logger.info("=====================")
answer2 = answer_service.generate_2.generate_answer(question2)
logger.info("question2: "+str(question2))
logger.info("answer2:" +str(answer2))



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

