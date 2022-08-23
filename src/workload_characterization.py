import calendar
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import typer
from sqlalchemy import Column, Integer, DateTime

from configuration_handler import WorkloadCharacterizationConfigHandler
from database import Database
from utils import get_date_from_string

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)


class WorkloadCharacterization:
    __database: Database
    __mapping: dict
    __remove_response_time_outliers: bool

    def __init__(self, database, config_handler, remove_response_time_outliers):
        self.__database = database
        self.__mapping = database.get_int_cmd_dict()
        self.__config_handler = config_handler
        self.__remove_response_time_outliers = remove_response_time_outliers

    def start_characterization(self):
        logging.info("begin loading data from db")
        timestamp_col = Column("Timestamp", DateTime)
        cmd_col = Column("cmd", Integer)
        response_time_col = Column("response time", Integer)
        training_data_db_result = self.__database.get_training_data_cursor_result(
            [timestamp_col, cmd_col, response_time_col]
        )
        training_data = pd.DataFrame.from_records(
            training_data_db_result,
            index="index",
            columns=["index", "Timestamp", "cmd", "response time"]
        )
        training_data = training_data.sort_values("response time", ascending=False)
        if self.__remove_response_time_outliers is True:
            training_data = self.__remove_outliers(training_data)

        training_data["weekday"] = training_data["Timestamp"].apply(
            lambda x: calendar.day_name[x.weekday()]
        )

        logging.info("start exporting charts")
        self.__export_charts(training_data)
        logging.info("start exporting excel")
        self.__export_excel(training_data)

    def __remove_outliers(self, training_data, std_threshold: int = 3):
        logging.info("removing response time outliers")
        row_count_before = training_data.__len__()
        training_data = training_data[
            np.abs(training_data["response time"] - training_data["response time"].mean()) <= (
                    std_threshold * training_data["response time"].std())]
        row_count_after = training_data.__len__()
        logging.info("removed {} of {} rows".format(row_count_before - row_count_after, row_count_before))
        return training_data

    def __format_request_type(self, int_cmd):
        return self.__mapping[int_cmd]

    def __get_request_rates_df(self, training_data: pd.DataFrame):
        training_data_statistic_df = training_data[["Timestamp", "cmd"]].rename(
            columns={"cmd": "count"}
        )
        requests_per_second = training_data_statistic_df.groupby(
            pd.Grouper(key="Timestamp", freq="1S")
        ).count()
        requests_per_minute = training_data_statistic_df.groupby(
            pd.Grouper(key="Timestamp", freq="1T")
        ).count()
        requests_per_hour = training_data_statistic_df.groupby(
            pd.Grouper(key="Timestamp", freq="1H")
        ).count()

        requests_per_interval_dict = {
            "frequency": ["sec", "min", "hour"],
            "median": [requests_per_second["count"].median(),
                       requests_per_minute["count"].median(),
                       requests_per_hour["count"].median()],
            "mean": [requests_per_second["count"].mean(),
                     requests_per_minute["count"].mean(),
                     requests_per_hour["count"].mean()],
            "min": [requests_per_second["count"].min(),
                    requests_per_minute["count"].min(),
                    requests_per_hour["count"].min()],
            "max": [requests_per_second["count"].max(),
                    requests_per_minute["count"].max(),
                    requests_per_hour["count"].max()],
        }
        df_frequency = pd.DataFrame.from_dict(requests_per_interval_dict)
        return df_frequency

    def __get_request_type_response_time_df(self, training_data: pd.DataFrame):
        request_types_with_response_time: pd.DataFrame = training_data[
            ["cmd", "response time"]].reset_index().drop(columns=["index"])
        request_types_with_response_time["cmd"] = \
            request_types_with_response_time["cmd"].apply(
                self.__format_request_type
            )
        request_types_with_response_time_mean: pd.DataFrame = request_types_with_response_time.groupby(
            ["cmd"]
        ).mean()
        request_types_with_response_time_median: pd.DataFrame = request_types_with_response_time.groupby(
            ["cmd"]
        ).median()
        request_types_with_response_time_min: pd.DataFrame = request_types_with_response_time.groupby(
            ["cmd"]
        ).min()
        request_types_with_response_time_max: pd.DataFrame = request_types_with_response_time.groupby(
            ["cmd"]
        ).max()
        request_types_count_requests: pd.DataFrame = request_types_with_response_time.groupby(
            ["cmd"]
        ).count()

        request_types_with_response_time_mean.rename(
            columns={"response time": "mean"},
            inplace=True
        )
        request_types_with_response_time_mean["median"] = \
            request_types_with_response_time_median["response time"]
        request_types_with_response_time_mean["min"] = \
            request_types_with_response_time_min["response time"]
        request_types_with_response_time_mean["max"] = \
            request_types_with_response_time_max["response time"]
        request_types_with_response_time_mean["count"] = \
            request_types_count_requests["response time"]

        return request_types_with_response_time_mean

    def __get_export_date_suffix(self):
        db_path = Path(self.__config_handler.get_db_url())
        return get_date_from_string(db_path.stem)

    def __get_export_name_outlier_str(self):
        outlier_str = "removed_outliers"
        if not self.__remove_response_time_outliers:
            outlier_str = "with_outliers"
        return outlier_str

    def __export_excel(self, training_data: pd.DataFrame):
        request_rates_df = self.__get_request_rates_df(training_data)
        request_types_response_time_df = self.__get_request_type_response_time_df(training_data)
        filename = "statistics_" + self.__get_export_name_outlier_str() + "_for_db_" + self.__get_export_date_suffix() + ".xlsx"
        filepath = Path(self.__config_handler.get_export_folder()) / filename
        excel_writer = pd.ExcelWriter(path=filepath, engine="xlsxwriter")
        request_types_response_time_df.to_excel(
            excel_writer,
            sheet_name="request types response time"
        )
        request_rates_df.to_excel(excel_writer, sheet_name="requests per frequency")
        excel_writer.save()

    def __export_charts(self, training_data: pd.DataFrame):
        training_data = training_data.drop("response time", axis=1)
        training_data["hour"] = training_data["Timestamp"].apply(lambda x: x.hour)
        training_data = training_data.rename(columns={"cmd": "count"})
        requests_per_hour = training_data.groupby(["weekday", "hour"]).count()
        requests_per_hour.reset_index(inplace=True)

        fig_requests_per_hour = px.bar(requests_per_hour, x="hour", y="count", color="weekday", barmode="group")
        fig_requests_per_hour.update_xaxes(type="category")
        request_per_hour_filename = "rph_" + self.__get_export_name_outlier_str() + "_for_db_" + self.__get_export_date_suffix() + ".pdf"
        filepath = Path(self.__config_handler.get_export_folder()) / request_per_hour_filename
        fig_requests_per_hour.write_image(filepath)

        requests_count_per_day = training_data[
            ["weekday", "Timestamp"]].groupby(["weekday"]).count().rename(
            columns={"Timestamp": "count"}
        ).reset_index()
        fig_req_per_day = px.bar(
            requests_count_per_day,
            y="count",
            x="weekday",
            orientation="v",
            text="count"
        )
        fig_req_per_day.update_xaxes(type="category")
        req_per_day = "rpd_" + self.__get_export_name_outlier_str() + "_for_db_" + self.__get_export_date_suffix() + ".pdf"
        filepath = Path(self.__config_handler.get_export_folder()) / req_per_day
        fig_req_per_day.write_image(filepath)


def main(
        config_file_path: str = "resources/config/characterization_config.json", remove_response_time_outliers: bool = False
):
    config_handler = WorkloadCharacterizationConfigHandler(config_file_path)
    config_handler.load_config()
    database = Database(config_handler)

    workload_characterization = WorkloadCharacterization(database, config_handler, remove_response_time_outliers)
    workload_characterization.start_characterization()


if __name__ == "__main__":
    typer.run(main)
