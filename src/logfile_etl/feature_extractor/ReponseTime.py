from src.logfile_etl.ParallelCommandsTracker import ParallelCommandsTracker
from src.logfile_etl.feature_extractor.AbstractFeatureExtractor import (
    AbstractFeatureExtractor,
)


class ResponseTime(AbstractFeatureExtractor):
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
