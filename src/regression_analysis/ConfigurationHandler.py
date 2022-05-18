import logging
from pathlib import Path

from src.Utils import get_project_root
import json


class ConfigurationHandler:
    def __init__(self, config_file_path: str):
        self.__y = None
        self.__models = None
        self.__db_path = None
        self.__features = None
        self.__config_file_path = config_file_path

    def load_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            config = json.load(config_file)
            self.__db_path = config["db"]
            self.__features = config["features"]
            self.__models = config["models"]
            self.__y = config["y"]

        self.__log_config()

    def get_features(self):
        return self.__features

    def get_db_url(self):
        Path(self.__db_path).parent.mkdir(parents=True, exist_ok=True)
        return "sqlite:///" + self.__db_path

    def __log_config(self):
        logging.info("Configuration successfully loaded")
        logging.info("db path: {}".format(self.__db_path))
        logging.info("features: {}".format(self.__features))
        logging.info("models: {}".format(self.__models))

    def get_models(self):
        return self.__models

    def get_y_column_name(self):
        return self.__y
