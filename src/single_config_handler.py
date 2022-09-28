import json
import logging
from pathlib import Path

import sys

from src.dto.dtos import ConfigFile
from src.utils import get_project_root

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)
handler = logging.StreamHandler(sys.stdout)


class ConfigurationHandler:
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

    def get_db_limit(self):
        return self.__config.database.limit

    def get_db_url(self):
        db_path = Path(self.__config.database.folder) / self.__config.database.name
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return "sqlite:///" + db_path.as_posix()

    ##################################################################
    ############################    ETL   ############################
    ##################################################################

    def get_unprocessed_logfile_dir(self):
        return Path(self.__config.logfile.unprocessed_logfiles)

    def get_processed_logfile_dir(self):
        return Path(self.__config.logfile.processed_logfiles)

    def get_db_config(self):
        return self.__config.logfile.db_export_folder

    def get_extractors(self):
        return self.__config.logfile.extractors

    def get_force(self):
        return self.__config.logfile.force

    ##################################################################
    ##########################    Analysis   #########################
    ##################################################################

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

    def use_feature_selection(self):
        return self.__config.analysis.estimator_handler.uses_feature_selector()

    # TODO refactore to return initialized feature extractors
    def get_feature_extractor_names(self):
        return self.__config.analysis.features

    def get_config(self):
        root_dir = get_project_root()
        abs_file_path = root_dir / self.__config_file_path
        with open(abs_file_path) as config_file:
            json_obj = json.load(config_file)
            return json_obj

    ##################################################################
    #########################    Workload    #########################
    ##################################################################

    def get_export_folder(self):
        return self.__config.workload.export_folder
