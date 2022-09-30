import pandas as pd
from sqlalchemy import Column, Integer, Float

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractETLFeatureExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ResponseTimeMilliSecAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column("response time", Integer)


class ResponseTimeSecAnalysisExtractor(AbstractAnalysisFeatureExtractor):

    def get_column(self) -> Column:
        return Column("response time", Float)

    def df_post_creation_hook(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.get_column_name()].fillna(value=0, axis=0, inplace=True)
        return df.astype(float)

    def get_df(self) -> pd.DataFrame:
        result_data = self.get_column_data(self.get_column())
        array = []
        for index, col in result_data:
            array.append(col / 1000)

        df = pd.DataFrame(array, dtype=float, columns=[self.get_column_name()])
        return df


class ResponseTimeETLExtractor(AbstractETLFeatureExtractor):
    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        delta = (
                parallel_commands_tracker[tid]["respondedAt"]
                - parallel_commands_tracker[tid]["receivedAt"]
        )
        return delta.total_seconds() * 1000
