from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractETLFeatureExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ArriveTimeAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)


class ArriveTimeETLExtractor(AbstractETLFeatureExtractor):
    intervals_per_hour = 4
    minutes_per_interval = 60 / intervals_per_hour

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        # received_at = datetime.datetime.strptime(parallel_commands_tracker[tid]["receivedAt"], "%Y-%m-%d %H:%M:%S")
        return int(
            parallel_commands_tracker[tid]["receivedAt"].hour
        ) * self.intervals_per_hour + int(
            parallel_commands_tracker[tid]["receivedAt"].minute
        ) // self.minutes_per_interval
