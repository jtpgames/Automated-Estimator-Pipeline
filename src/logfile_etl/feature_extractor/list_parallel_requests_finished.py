import json

from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker
from src.logfile_etl.feature_extractor.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)


class ListParallelRequestsFinished(AbstractFeatureExtractor):
    def get_feature_name(self) -> str:
        return "List parallel requests finished"

    def extract_feature(
        self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return json.dumps(parallel_commands_tracker[tid]["listParallelCommandsFinished"])
