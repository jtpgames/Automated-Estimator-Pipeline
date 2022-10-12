from sqlalchemy import Column, DateTime

from src.feature_extractor.abstract_feature_extractor import (
    AbstractETLFeatureExtractor,
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class TimestampETLExtractor(AbstractETLFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_feature_name(), DateTime)

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["receivedAt"]
