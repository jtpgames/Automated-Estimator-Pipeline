import logging
from pathlib import Path

from src.utils import get_project_root
import json


class ConfigurationHandler:
    def __init__(self, config_file_path: str):
        self.__model_save_path = None
        self.__y = None
        self.__models = None
        self.__db_path = None
        self.__features = None
        self.__config_file_path = config_file_path
        self.__db_limit = -1

    def load_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            config = json.load(config_file)
            self.__db_path = config["db"]
            self.__features = config["features"]
            self.__models = config["models"]
            self.__y = config["y"]
            self.__model_save_path = config["model_save_path"]
            self.__db_limit = config["db_limit"]

        self.__log_config()

    def get_features(self):
        return self.__features

    def get_db_url(self):
        Path(self.__db_path).parent.mkdir(parents=True, exist_ok=True)
        return "sqlite:///" + self.__db_path

    def __log_config(self):
        logging.info(
            "################################################################"
        )
        logging.info(
            "################ Configuration successfully loaded #############"
        )
        logging.info(
            "################################################################\n"
        )
        logging.info("db path: {}".format(self.__db_path))
        logging.info("features: {}".format(self.__features))
        logging.info("y column: {}".format(self.__y))
        logging.info("models: {}".format(self.__models))
        logging.info("db limit: {}\n".format(self.__db_limit))

    def get_models(self):
        return self.__models

    def get_y_column_name(self):
        return self.__y

    def get_model_save_path(self):
        return self.__model_save_path

    def get_db_limit(self):
        return self.__db_limit
