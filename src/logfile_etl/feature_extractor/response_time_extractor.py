from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker
from src.logfile_etl.feature_extractor.abstract_feature_extractor import (
    AbstractFeatureETLExtractor,
)


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
