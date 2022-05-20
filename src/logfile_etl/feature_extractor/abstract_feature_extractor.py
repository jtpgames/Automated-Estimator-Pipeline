from abc import ABC

from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class AbstractFeatureExtractor(ABC):
    def get_feature_name(self) -> str:
        pass

    def extract_feature(
        self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        pass
