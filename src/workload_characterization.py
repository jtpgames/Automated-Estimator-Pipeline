from pathlib import Path

import pandas as pd
import plotly.express as px
import typer
from sqlalchemy import Column, Integer, DateTime

from configuration_handler import WorkloadCharacterizationConfigHandler
from database import Database


class WorkloadCharacterization:
    __database: Database
    __mapping: dict

    def __init__(self, database, config_handler):
        self.__database = database
        self.__mapping = database.get_int_cmd_dict()
        self.__config_handler = config_handler

    def format_request_type(self, int_cmd):
        return self.__mapping[int_cmd]

    def start(self):
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
        print(training_data)
        training_data["weekday"] = training_data["Timestamp"].apply(
            lambda x: x.weekday()
        )

        # request types per day
        request_types_group: pd.DataFrame = training_data[
            ["cmd", "weekday", "Timestamp"]].groupby(
            ["cmd", "weekday"]
        ).count().rename(columns={"Timestamp": "Count"}).sort_values(
            by=["Count"],
            ascending=False
        ).reset_index()

        print(request_types_group)
        request_types_group["cmd"] = request_types_group["cmd"].apply(
            self.format_request_type
        )
        fig = px.bar(
            request_types_group,
            y="weekday",
            x="Count",
            color="cmd",
            orientation="h"
        )
        # fig.show()

        # request count per day

        requests_count_per_day = training_data[
            ["weekday", "Timestamp"]].groupby(["weekday"]).count().rename(
            columns={"Timestamp": "Count"}
        ).reset_index()
        fig_req_per_day = px.bar(
            requests_count_per_day,
            y="Count",
            x="weekday",
            orientation="v",
            text="Count"
        )
        fig_req_per_day.update_xaxes(type="category")
        # fig_req_per_day.show()

        # print("==== requests")
        # print(request_types_group)
        # print("==== 25 most executed requests")
        # print(request_types_group.head(25))
        # print("==== Number of different requests: %i" % len(request_types_group))

        training_data_stastic_df = training_data[["Timestamp", "cmd"]].rename(
            columns={"cmd": "count"}
        )

        # requeststypes after mean, median, min, max response time (number of groups fix and variable)
        request_types_with_response_time: pd.DataFrame = training_data[
            ["cmd", "response time"]].reset_index().drop(columns=["index"])
        request_types_with_response_time["cmd"] = \
            request_types_with_response_time["cmd"].apply(
                self.format_request_type
            )

        # create one df with all aggregates

    def __export_excel(self, training_data: pd.DataFrame):
        # requests per sec, min, hour
        training_data_stastic_df = training_data[["Timestamp", "cmd"]].rename(
            columns={"cmd": "count"}
        )
        requests_per_second = training_data_stastic_df.groupby(
            pd.Grouper(key="Timestamp", freq="1s")
        ).count()
        interval_begin = training_data["Timestamp"].min()
        interval_end = training_data["Timestamp"].max()
        requests_per_minute = training_data_stastic_df.groupby(
            pd.Grouper(key="Timestamp", freq="1m")
        ).count()
        requests_per_hour = training_data_stastic_df.groupby(
            pd.Grouper(key="Timestamp", freq="1h")
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

        # requeststypes after mean, median, min, max response time (number of groups fix and variable)
        request_types_with_response_time: pd.DataFrame = training_data[
            ["cmd", "response time"]].reset_index().drop(columns=["index"])
        request_types_with_response_time["cmd"] = \
            request_types_with_response_time["cmd"].apply(
                self.format_request_type
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
        # request_types_with_response_time_mean.to_excel("request_types_with_response_times.xlsx")
        filename = "statistics.xlsx"
        filepath = Path(self.__config_handler.get_export_folder()) / filename
        excel_writer = pd.ExcelWriter(path=filepath, engine="xlsxwriter")
        request_types_with_response_time_mean.to_excel(
            excel_writer,
            sheet_name="request types response time"
        )
        df_frequency.to_excel(excel_writer, sheet_name="requests per frequency")
        excel_writer.save()

    def __export_charts(self, training_data: pd.DataFrame):
        pass

    def start_characterization(self):
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
        training_data["weekday"] = training_data["Timestamp"].apply(
            lambda x: x.weekday()
        )

        print("start exporting charts")
        self.__export_charts(training_data)
        print("start exporting excel")
        self.__export_excel(training_data)


def main(
        config_file_path: str = "resources/config/characterization_config.json"
):
    config_handler = WorkloadCharacterizationConfigHandler(config_file_path)
    config_handler.load_config()
    database = Database(config_handler)

    regression_analysis = WorkloadCharacterization(database, config_handler)
    regression_analysis.start_characterization()


if __name__ == "__main__":
    typer.run(main)
