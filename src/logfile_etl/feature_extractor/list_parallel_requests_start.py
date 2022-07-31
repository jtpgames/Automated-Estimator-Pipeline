import json

from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker
from src.logfile_etl.feature_extractor.abstract_feature_extractor import (
    AbstractFeatureETLExtractor,
)


class ListParallelRequestsStartETLExtractor(AbstractFeatureETLExtractor):
    def get_feature_name(self) -> str:
        return "List parallel requests start"

    def extract_feature(
        self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return json.dumps(parallel_commands_tracker[tid]["listParallelCommandsStart"])
