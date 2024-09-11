import logging

def setup_logging():
    """
    Setup logging for all modules of this project.
    """

    default_loglevel = logging.INFO
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(filename)s:%(funcName)s() - %(message)s',
        level=default_loglevel,
        datefmt='%Y-%m-%d %H:%M:%S')

    # Set different levels for different modules
    logging.getLogger('exported_api').setLevel(logging.DEBUG)
    logging.getLogger('factory').setLevel(logging.DEBUG)
    logging.getLogger('rag_index_service').setLevel(logging.DEBUG)
    logging.getLogger('rag_response_service').setLevel(logging.DEBUG)
    logging.getLogger('rag_workflow').setLevel(logging.DEBUG)
    logging.getLogger('service').setLevel(logging.DEBUG)

    logging.getLogger('test').setLevel(logging.DEBUG)
    logging.getLogger('test_data_gen').setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    logger.info("Logging setup done")
