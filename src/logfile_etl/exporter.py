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
    def export(self, data: dict):
        logging.info("Start exporting extracted features")
        logging.info(
            "Export methods: {}".format(self.__config_handler.get_export_methods())
        )
        for entry in self.__config_handler.get_export_methods():
            if entry == "db":
                self.to_db(data)
            if entry == "csv":
                self.to_csv(data)

    def to_csv(self, data: dict):
        df = pd.DataFrame(data)
        csv_config = self.__config_handler.get_csv_config()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file_name = "trainingdata_{}.csv".format(today)
        save_path = Path(csv_config["folder"]) / file_name

        Path(csv_config["folder"]).mkdir(parents=True, exist_ok=True)

        df.to_csv(save_path, sep=";")

    def to_db(self, data: dict):
        df = pd.DataFrame(data)
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
        df.to_sql("gs_training_data", con=con, if_exists="replace")
