import pandas as pd
from sqlalchemy import Column, Integer

from feature_extractor.encoder.seconds_encoder import MilliSecondsEncoder
from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractETLFeatureExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ResponseTimeMilliSecAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column("response_time", Integer)


class ResponseTimeSecAnalysisExtractor(AbstractAnalysisFeatureExtractor):

    def get_column(self) -> Column:
        return Column("response_time", MilliSecondsEncoder)

    def df_post_creation_hook(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.astype(float)


class ResponseTimeETLExtractor(AbstractETLFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_feature_name(), Integer)

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        delta = (
                parallel_commands_tracker[tid]["respondedAt"]
                - parallel_commands_tracker[tid]["receivedAt"]
        )
        return delta.total_seconds() * 1000
