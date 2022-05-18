from sqlalchemy import create_engine

from src.regression_analysis.ConfigurationHandler import ConfigurationHandler


class Database:
    def __init__(self, config_handler: ConfigurationHandler):
        self.__db_url = config_handler.get_db_url()

    def connection(self):
        return create_engine(self.__db_url)
