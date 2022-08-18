import logging
from abc import ABC, abstractmethod
from pathlib import Path

from src.utils import get_project_root
import json


class BaseConfigurationHandler(ABC):
    @abstractmethod
    def get_db_url(self) -> str:
        pass

    @abstractmethod
    def get_db_limit(self) -> int:
        pass


class AnalysisConfigurationHandler(BaseConfigurationHandler):
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


class ETLConfigurationHandler:
    def __init__(self, config_file_path: str):
        self.__force = False
        self.__extractors = []
        self.__csv_config = None
        self.__db_config = None
        self.__export_methods = []
        self.__processed_logfile_dir = ""
        self.__unprocessed_logfile_dir = ""
        self.__config_file_path = config_file_path

    def load_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            config = json.load(config_file)

            self.__unprocessed_logfile_dir = config["unprocessed_logfiles"]
            self.__processed_logfile_dir = config["processed_logfiles"]
            self.__export_methods = config["export_methods"]
            self.__db_config = config["db"]
            self.__csv_config = config["csv"]
            self.__extractors = config["extractors"]
            self.__force = config["force"]

        self.__log_config()

    def get_unprocessed_logfile_dir(self):
        return Path(self.__unprocessed_logfile_dir)

    def get_processed_logfile_dir(self):
        return Path(self.__processed_logfile_dir)

    def get_export_methods(self):
        return self.__export_methods

    def get_db_config(self):
        return self.__db_config

    def get_csv_config(self):
        return self.__csv_config

    def get_extractors(self):
        return self.__extractors

    def get_force(self):
        return self.__force

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
        logging.info(
            "Directory for unprocessed logfile: {}".format(
                self.__unprocessed_logfile_dir
            )
        )
        logging.info(
            "Directory for processed logfile: {}".format(
                self.__processed_logfile_dir
            )
        )
        logging.info("Loaded export methods: {}".format(self.__export_methods))
        logging.info(
            "Loaded feature extractors by column name: {}".format(
                self.__extractors
            )
        )
        logging.info("Force parameter is set to: {}\n".format(self.__force))


class WorkloadCharacterizationConfigHandler(BaseConfigurationHandler):
    def __init__(self, config_file_path: str):
        self.__export_folder = None
        self.__db_path = None
        self.__db_limit = -1
        self.__config_file_path = config_file_path

    def load_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            config = json.load(config_file)
            self.__db_path = config["db"]
            self.__db_limit = config["db_limit"]
            self.__export_folder = config["export_folder"]

        self.__log_config()

    def get_db_limit(self):
        return self.__db_limit

    def get_db_url(self):
        Path(self.__db_path).parent.mkdir(parents=True, exist_ok=True)
        return "sqlite:///" + self.__db_path

    def get_export_folder(self):
        return self.__export_folder

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
        logging.info(
            "db to load workload characterization from: {}\n".format(
                self.__db_path
            )
        )
        logging.info("db limit: {}\n".format(self.__db_limit))
        logging.info("export folder: {}\n".format(self.__export_folder))
