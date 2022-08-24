import logging
from abc import ABC, abstractmethod
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor

from src.utils import get_project_root
import json

from typing import List, Any

from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso, ElasticNet,
)
from sklearn.tree import DecisionTreeRegressor

possible_estimators = [
    ("LR", LinearRegression()),
    ("Ridge", Ridge()),
    ("Lasso", Lasso()),
    ("DT", DecisionTreeRegressor()),
    ("ElasticNet", ElasticNet()),
    ("RF", RandomForestRegressor())
]


def get_model_object_from_name(estimator_name: str) -> Any:
    for x, estimator in possible_estimators:
        if estimator_name == x:
            return estimator
    # TODO raise error
    return ""


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

    def str(self):
        return self.__name



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
        self.__pipeline = None
        self.__grid_search = None
        self.__estimators: List[EstimatorWrapper] = []
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
            self.__db_limit = config["db_limit"]
            self.__y = config["y"]
            self.__estimators = self.__get_estimators_from_config(config["estimators"])
            self.__pipeline = config["pipeline"]
            self.__grid_search = config["grid_search"]
            self.__model_save_path = config["model_save_path"]

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
        logging.info("models: {}".format(self.__estimators))
        logging.info("db limit: {}\n".format(self.__db_limit))
        logging.info("pipeline: {}\n".format(self.__pipeline))
        logging.info("grid search: {}\n".format(self.__grid_search))

    def get_estimators(self):
        return self.__estimators

    def get_y_column_name(self):
        return self.__y

    def get_model_save_path(self):
        return self.__model_save_path

    def get_db_limit(self):
        return self.__db_limit

    def __get_estimators_from_config(self, param):
        estimators = []
        for estimator_config in param:
            name = estimator_config["name"]
            estimator = get_model_object_from_name(name)
            grid_dict = {}
            if "grid_dict" in estimator_config:
                grid_dict = estimator_config["grid_dict"]
            wrapper = EstimatorWrapper(name, estimator, grid_dict)
            estimators.append(wrapper)
        return estimators

    def get_grid_search_parameter(self):
        return self.__grid_search

    def get_pipeline_parameters(self):
        return self.__pipeline

    def use_feature_selection(self):
        return "feature_selection" in self.__pipeline


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


