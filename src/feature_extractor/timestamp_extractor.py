from src.feature_extractor.abstract_feature_extractor import (
    AbstractFeatureETLExtractor,
)

from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class TimestampETLExtractor(AbstractFeatureETLExtractor):
    def get_feature_name(self) -> str:
        return "Timestamp"

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["receivedAt"].strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
