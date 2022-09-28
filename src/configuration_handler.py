import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path

import typer

from dto.dtos import ConfigFile
from src.utils import get_project_root


class EstimatorWrapper:
    __name: str
    __estimator: any
    __parameter: dict

    def __init__(self, name, estimator, parameter=None):
        if parameter is None:
            parameter = {}
        self.__name = name
        self.__estimator = estimator
        self.__parameter = parameter

    def get_name(self):
        return self.__name

    def get_estimator(self):
        return self.__estimator

    def get_parameter(self):
        return self.__parameter

    def __str__(self):
        return self.__name


class BaseConfigurationHandler(ABC):
    @abstractmethod
    def get_db_url(self) -> str:
        pass

    @abstractmethod
    def get_db_limit(self) -> int:
        pass


class AnalysisConfigurationHandler(BaseConfigurationHandler):
    __config_file_path: str
    __config: ConfigFile

    def __init__(self, config_file_path: str):
        self.__config = None
        self.__config_file_path = config_file_path

    def load_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            json_obj = json.load(config_file)
            self.__config = ConfigFile.Schema().load(json_obj)
            self.__log_config()

    # TODO refactore to return initialized feature extractors
    def get_feature_extractor_names(self):
        return self.__config.analysis.features

    def get_db_url(self) -> str:
        db_url = "sqlite:///" + self.__config.database.folder + "/" + self.__config.database.name
        print(db_url)
        return "sqlite:///" + self.__config.database.folder + "/" + self.__config.database.name

    def get_db_limit(self) -> int:
        return self.__config.database.limit

    def get_estimator_handler(self):
        return self.__config.analysis.estimator_handler

    def get_y_column_name(self):
        return self.__config.analysis.y

    def get_model_save_path(self):
        return self.__config.analysis.model_save_path

    def get_grid_search_dict(self):
        return self.__config.analysis.estimator_handler.get_params()

    def get_outlier_detection_type(self):
        return self.__config.analysis.outlier_detection_based_on_cmd_type

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
        # TODO find a way to pretty print with logging
        print(json.dumps(ConfigFile.Schema().dump(self.__config), indent=4))

    def use_feature_selection(self):
        return self.__config.analysis.estimator_handler.uses_feature_selector()

    def get_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            json_obj = json.load(config_file)
            return json_obj


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


def main(
        config_file_path: str = "resources/config/analysis_config.json"
):
    config_handler = AnalysisConfigurationHandler(config_file_path)
    config_handler.load_config()
    # database = Database(config_handler)
    #
    # regression_analysis = RegressionAnalysis(config_handler, database)
    # regression_analysis.start()


if __name__ == "__main__":
    typer.run(main)
