import pandas as pd
from abc import ABC, abstractmethod
from numpy import short
from sqlalchemy import Column
from src.database import Database

from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker

trainings_data_table_name = "gs_training_data"
cmd_mapping_table_name = "gs_training_cmd_mapping"


class AbstractAnalysisFeatureExtractor(ABC):

    def __init__(self, db: Database, column_name):
        self.__db = db
        self.__column_name = column_name

    @abstractmethod
    def get_column(self) -> Column:
        pass

    def get_column_name(self) -> str:
        return self.__column_name

    # TODO change name
    def df_post_production(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.get_column_name()].fillna(value=0, axis=0, inplace=True)
        return df.astype(short)

    def get_df(self) -> pd.DataFrame:
        result = self.__db.get_training_data_from_db(self.get_column())
        df = self.get_df_from_db_column_data(result)
        return self.df_post_production(df)

    def get_df_from_db_column_data(self, db_result):
        return pd.DataFrame.from_records(
            db_result,
            index='index',
            columns=['index', self.get_column_name()]
        )

    def get_column_data(self, column):
        print(column)
        return self.__db.get_training_data_from_db(column).all()

    def get_cmd_names_mapping(self):
        return self.__db.get_cmd_names_dict()


class AbstractETLFeatureExtractor(ABC):
    def __init__(self, feature_name):
        self.__feature_name = feature_name

    def get_feature_name(self) -> str:
        return self.__feature_name

    @abstractmethod
    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        pass
