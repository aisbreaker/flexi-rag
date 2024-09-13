from functools import cache

# partitially based on idea of
#   https://stackoverflow.com/questions/52534211/python-type-hinting-with-db-api/77350678#77350678 and
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection, DBAPICursor
else:
    DBAPIConnection = any
    DBAPICursor = any

from factory.factory_util import call_function_or_constructor
from service.configloader import deep_get, settings
import logging

logger = logging.getLogger(__name__)


#
# SQL database instance and its setup.
#
# Uses PEP 249 - Database API Specification 2.0 - https://peps.python.org/pep-0249/
#

@cache
def get_sql_database_connection() -> DBAPIConnection:
    # Start
    config_sql_database = deep_get(settings, "config.common.databases.sql_database")
    context_str_for_logging = f"Setup SQL Database connection: {config_sql_database}"
    logger.info(context_str_for_logging)

    # Load config
    module_and_connect_func = deep_get(config_sql_database, "connect")
    connect_func_kwargs     = deep_get(config_sql_database, "args")

    # Action: Create instance
    return call_function_or_constructor(module_and_connect_func, connect_func_kwargs, context_str_for_logging)
