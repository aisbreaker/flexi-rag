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




# start server with API?
if True:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from api import endpoints
    from api import admin_endpoints

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

    # /* for static files
    app.mount("/", StaticFiles(directory="static",html = True), name="static")


    # run the HTTP server
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)


#
# some test code
#
test_queries = False

if test_queries:
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
