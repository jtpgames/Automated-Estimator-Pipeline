import logging
from abc import ABC, abstractmethod
from dataclasses import field
from pathlib import Path

import typer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from marshmallow_dataclass import dataclass
from typing import Union

from sklearn.feature_selection import SelectFromModel, SelectKBest, SelectPercentile
from sklearn.preprocessing import StandardScaler

from src.utils import get_project_root
from typing import List, Any, Optional, ClassVar, Type
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso, ElasticNet, SGDRegressor,
)
from sklearn.tree import DecisionTreeRegressor
from marshmallow import Schema
import json

possible_estimators = [
    ("LR", LinearRegression),
    ("Ridge", Ridge),
    ("Lasso", Lasso),
    ("DT", DecisionTreeRegressor),
    ("ElasticNet", ElasticNet),
    ("RF", RandomForestRegressor),
    ("SGDR", SGDRegressor)
]


def get_estimater_class_from_name(estimator_name: str) -> Any:
    for x, estimator in possible_estimators:
        if estimator_name == x:
            return estimator
    # TODO raise error
    return None


possible_actions = [
    ("std", StandardScaler),
    ("pca", PCA),
    ("select_from_model", SelectFromModel),
    ("k_best", SelectKBest),
    ("percentile", SelectPercentile)
]


def get_action_class_from_name(action_name: str):
    for x, action in possible_actions:
        if action_name == x:
            return action
    # TODO raise error
    return None


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


@dataclass
class GridSearch:
    scoring: Union[str, list[str]]
    refit: Optional[str]
    verbose: Optional[int] = 1
    n_jobs: Optional[int] = None
    pre_dispatch: Union[Optional[int], Optional[str]] = "2*n_jobs"


@dataclass
class Estimator:
    name: str
    params: dict


@dataclass
class PipelineStep:
    step: str
    action: str
    params: dict
    needs_estimator: Optional[bool] = False


@dataclass
class Pipeline:
    for_estimators: Optional[list[str]] = field(default_factory=list)
    steps: list[PipelineStep] = field(default_factory=list)


@dataclass
class CrossValidation:
    n_splits: Optional[int] = 5
    shuffle: Optional[bool] = True
    random_state: Optional[int] = 42


@dataclass
class EstimatorHandler:
    pipelines: list[Pipeline]
    grid_search: GridSearch
    estimators: list[Estimator]
    cross_validation: Optional[CrossValidation]

    def __set_pipeline_for_estimators(self):
        if len(self.pipelines) == 1:
            self.pipelines[0].for_estimators = [estimator.name for estimator in self.estimators]

    def get_params(self):
        all_step_names = []
        parameter_grid = []
        self.__set_pipeline_for_estimators()
        for estimator_config in self.estimators:
            estimator = get_estimater_class_from_name(estimator_config.name)()
            params_to_rename = estimator_config.params
            params = {"estimator": [estimator]}

            for pipeline in self.pipelines:
                if estimator_config.name in pipeline.for_estimators:
                    for step in pipeline.steps:
                        # pipeline step name with prefix for compatible estimators e.g. dt_linear_scaler
                        step_prefix = "_".join(pipeline.for_estimators) + "_"
                        step_name = step_prefix + step.step

                        # add step name to all pipeline steps list if not already present
                        if step_name not in all_step_names:
                            all_step_names.append(step_name)

                        # initalize action with estimator as input if needed and add
                        # to the parameter grid of the estimator. e.g. dt_select_from_model: [SelectFromModel(estimator)]
                        action = get_action_class_from_name(step.action)
                        if step.needs_estimator:
                            params[step_name] = [action(estimator)]
                        else:
                            params[step_name] = [action()]

                        # add all remaining grid params with pipeline
                        for key, value in step.params.items():
                            params[step_name + "__" + key] = value

            for key, value in params_to_rename.items():
                params["estimator__" + key] = value

            parameter_grid.append(params)

        # add estimator as last pipeline step
        all_step_names.append("estimator")
        # all pipeline steps
        all_pipeline_steps = []
        for step in all_step_names:
            all_pipeline_steps.append((step, "passthrough"))

        return {"steps": all_pipeline_steps, "parameter_grid": parameter_grid,
                "grid_search_params": GridSearch.Schema().dump(self.grid_search),
                "cv_params": CrossValidation.Schema().dump(self.cross_validation)}

    def get_grid_search_parameter(self):
        # if multiple scoring metrices are defined, refit has to be set
        if self.grid_search.refit is not None:
            return {
                "key": "rank_test_" + self.grid_search.refit,
                "values": ["mean_test_" + x for x in self.grid_search.scoring],
                "names": self.grid_search.scoring
            }
        else:
            # if refit is not set, then scoring has to be a single value
            return {"key": "rank_test_score", "values": ["mean_test_score"],
                    "names": [self.grid_search.scoring]}

    def uses_feature_selector(self):
        pipeline_steps = [step.step for pipeline in self.pipelines for step in pipeline.steps]
        print("feature_selection" in pipeline_steps)
        return "feature_selection" in pipeline_steps


@dataclass
class ConfigFile:
    db: str
    db_limit: int
    features: list[str]
    y: str
    estimator_handler: EstimatorHandler
    model_save_path: str
    outlier_detection_based_on_cmd_type: bool


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
        return self.__config.features

    def get_db_url(self) -> str:
        return "sqlite:///" + self.__config.db

    def get_db_limit(self) -> int:
        return self.__config.db_limit

    def get_estimator_handler(self):
        return self.__config.estimator_handler

    def get_y_column_name(self):
        return self.__config.y

    def get_model_save_path(self):
        return self.__config.model_save_path

    def get_grid_search_dict(self):
        return self.__config.estimator_handler.get_params()

    def get_outlier_detection_type(self):
        return self.__config.outlier_detection_based_on_cmd_type

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
        return self.__config.estimator_handler.uses_feature_selector()

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
