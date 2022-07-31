from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractFeatureETLExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ResponseTimeAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)


class ResponseTimeETLExtractor(AbstractFeatureETLExtractor):
    def get_feature_name(self) -> str:
        return "response time"

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        delta = (
                parallel_commands_tracker[tid]["respondedAt"]
                - parallel_commands_tracker[tid]["receivedAt"]
        )
        return delta.total_seconds() * 1000
