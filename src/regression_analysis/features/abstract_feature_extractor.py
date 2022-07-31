from abc import ABC, abstractmethod

import pandas as pd
from numpy import short
from sqlalchemy import select, Table, Column, Integer, String, MetaData
from src.regression_analysis.database import Database


trainings_data_table_name = "gs_training_data"
cmd_mapping_table_name = "gs_training_cmd_mapping"

class AbstractFeatureExtractor(ABC):

    def __init__(self, db: Database, column_name):
        self.__db = db
        self.__column_name = column_name

    @abstractmethod
    def get_column(self) -> Column:
        pass

    def get_column_name(self) -> str:
        return self.__column_name

    # TODO change name
    def df_postproduction(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.get_column_name()].fillna(value=0, axis=0, inplace=True)
        return df.astype(short)

    def get_df(self) -> pd.DataFrame:
        result = self.__db.get_training_data_from_db(self.get_column())
        df = self.get_df_from_db_column_data(result)
        return self.df_postproduction(df)

    def get_df_from_db_column_data(self, db_result):
        return pd.DataFrame.from_records(
            db_result,
            index='index',
            columns=['index', self.get_column_name()]
        )

    def get_column_data(self, column):
        self.__db.get_training_data_from_db(column)


    def get_cmd_names_mapping(self):
        return self.__db.get_cmd_names_dict()



