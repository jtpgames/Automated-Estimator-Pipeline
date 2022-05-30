import datetime
import logging
from pathlib import Path
import platform

import pandas as pd
from sqlalchemy import create_engine
from src.logfile_etl.configuration_handler import ConfigurationHandler


class Exporter:
    def __init__(self, config_handler: ConfigurationHandler):
        self.__config_handler = config_handler

    # TODO make user directories exist
    def export(self, data: dict, mapping: dict):
        logging.info("Start exporting extracted features")
        logging.info(
            "Export methods: {}".format(
                self.__config_handler.get_export_methods()
            )
        )
        df_data = pd.DataFrame(data)
        df_mapping = pd.DataFrame.from_dict(
            mapping,
            orient="index",
            columns=["mapping"]
        )
        for entry in self.__config_handler.get_export_methods():
            if entry == "db":
                self.to_db(df_data, df_mapping)
            if entry == "csv":
                self.to_csv(df_data, df_mapping)

    def to_csv(self, df_data: pd.DataFrame, df_mapping: pd.DataFrame):
        csv_config = self.__config_handler.get_csv_config()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        data_file_name = "training_data_{}.csv".format(today)
        mapping_file_name = "training_mapping_{}.csv".format(today)
        data_save_path = Path(csv_config["folder"]) / data_file_name
        mapping_save_path = Path(csv_config["folder"]) / mapping_file_name

        Path(csv_config["folder"]).mkdir(parents=True, exist_ok=True)

        df_data.to_csv(data_save_path, sep=";")
        df_mapping.to_csv(mapping_save_path, sep=";")

    def to_db(self, df_data: pd.DataFrame, df_mapping: pd.DataFrame):
        db_config = self.__config_handler.get_db_config()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file_name = "trainingdata_{}.db".format(today)

        # makes sure that folder exists
        Path(db_config["folder"]).mkdir(parents=True, exist_ok=True)

        if platform.system() == "Windows":
            file_path = Path(db_config["folder"]) / file_name
            file_path_str = str(file_path.absolute())
            db_url = r"sqlite:///" + file_path_str

        else:
            file_path = Path(db_config["folder"]) / file_name
            db_url = "sqlite:////" + file_path.absolute().as_posix()

        con = create_engine(db_url)
        df_data.to_sql("gs_training_data", con=con, if_exists="replace")
        df_mapping.to_sql(
            "gs_training_cmd_mapping",
            con=con,
            if_exists="replace"
        )
