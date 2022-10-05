import json
import logging

from src.dto.dtos import ConfigFile, EstimatorPipelineDTO
from src.utils import get_project_root


class Configuration:
    __config_file_path: str
    __config: ConfigFile

    def __init__(self, config_file_path: str):
        self.__config = None
        self.__config_file_path = config_file_path

    def load(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            json_obj = json.load(config_file)
            self.__config = ConfigFile.Schema().load(json_obj)
            self.__log_config()

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
        logging.info(json.dumps(ConfigFile.Schema().dump(self.__config), indent=4))
        logging.info(
            "################################################################"
        )
        logging.info(
            "################################################################\n"
        )

    def for_estimator_pipeline(self) -> EstimatorPipelineDTO:
        return self.__config.estimator_pipe

    def for_outlier_detection(self):
        return self.__config.outlier_detection

    def for_database(self):
        return self.__config.database

    def for_logfile_etl(self):
        return self.__config.logfile_etl_pipe

    def for_workload_characterization(self):
        return self.__config.workload

    def get_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            json_obj = json.load(config_file)
            return json_obj
