import calendar
import logging
from pathlib import Path

import pandas as pd
import plotly.express as px
from sqlalchemy import Column, Integer, DateTime

from analysis.outlier_detection import OutlierDetection
from configuration import Configuration
from database import Database


class WorkloadCharacterization:
    __db: Database
    __mapping: dict
    __export_folder: str

    def __init__(self, config: Configuration):
        self.__db = Database(config.for_database())
        self.__mapping = self.__db.get_cmd_mapping(cmd_key=False)
        self.__outlier_detection = OutlierDetection(config.for_outlier_detection(), self.__db)
        self.__export_folder = config.for_workload_characterization().export_folder

    def run(self):
        logging.info("begin loading data from db")
        timestamp_col = Column("Timestamp", DateTime)
        cmd_col = Column("cmd", Integer)
        response_time_col = Column("response time", Integer)
        training_data_db_result = self.__db.get_training_data_cursor_result_columns(
            [timestamp_col, cmd_col, response_time_col]
        )
        training_data = pd.DataFrame.from_records(
            training_data_db_result,
            index="index",
            columns=["index", "Timestamp", "cmd", "response time"]
        )
        training_data = training_data.sort_values("response time", ascending=False)
        y = training_data.pop("response time")
        X, y = self.__outlier_detection.remove_outliers(training_data, y)
        training_data = X.merge(y, left_index=True, right_index=True)

        training_data["weekday"] = training_data["Timestamp"].apply(
            lambda x: calendar.day_name[x.weekday()]
        )

        logging.info("start exporting charts")
        self.__export_charts(training_data)
        logging.info("start exporting excel")
        self.__export_excel(training_data)

    def __format_request_type(self, int_cmd):
        return self.__mapping[int_cmd]

    @staticmethod
    def __get_request_rates_df(training_data: pd.DataFrame):
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

    def __get_filename_suffix(self):
        date = self.__db.get_date_from_db_name()
        infos = self.__outlier_detection.get_string_containing_outlier_info()
        return f"for_db_{date}_{infos}"

    def __export_excel(self, training_data: pd.DataFrame):
        request_rates_df = self.__get_request_rates_df(training_data)
        request_types_response_time_df = self.__get_request_type_response_time_df(training_data)
        filename = f"statistics_{self.__get_filename_suffix()}.xlsx"
        filepath = Path(self.__export_folder) / filename
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
        request_per_hour_filename = f"rph_{self.__get_filename_suffix()}.pdf"
        filepath = Path(self.__export_folder) / request_per_hour_filename
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
        req_per_day = f"rpd_{self.__get_filename_suffix()}.pdf"
        filepath = Path(self.__export_folder) / req_per_day
        fig_req_per_day.write_image(filepath)
