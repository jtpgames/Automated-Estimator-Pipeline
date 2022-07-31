import logging

from src.utils import get_project_root
from pathlib import Path
import json


class AnalysisConfigurationHandler:
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
