import pandas as pd
from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractETLFeatureExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class CMDAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)


class CMDOneHotAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column("cmd", Integer)

    def get_df(self) -> pd.DataFrame:
        result_data = self.get_column_data(self.get_column())
        df = self.get_df_from_db_column_data(result_data)
        data = pd.get_dummies(df, prefix=['cmd'], columns=['cmd one hot'], drop_first=True)
        return data


class CMDETLExtractor(AbstractETLFeatureExtractor):
    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["cmd"]
