from src.logfile_etl.ParallelCommandsTracker import ParallelCommandsTracker
from src.logfile_etl.feature_extractor.AbstractFeatureExtractor import (
    AbstractFeatureExtractor,
)


class Cmd(AbstractFeatureExtractor):
    def get_feature_name(self) -> str:
        return "cmd"

    def extract_feature(
        self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["cmd"]
