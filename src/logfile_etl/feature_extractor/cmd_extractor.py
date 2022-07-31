from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker
from src.logfile_etl.feature_extractor.abstract_feature_extractor import (
    AbstractFeatureETLExtractor,
)


class CMDETLExtractor(AbstractFeatureETLExtractor):
    def get_feature_name(self) -> str:
        return "cmd"

    def extract_feature(
        self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["cmd"]
