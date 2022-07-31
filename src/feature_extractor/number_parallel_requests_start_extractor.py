from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractFeatureETLExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class PROneAnalysisExtractor(AbstractAnalysisFeatureExtractor):

    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)


class ParallelRequestsOneETLExtractor(AbstractFeatureETLExtractor):
    def get_feature_name(self) -> str:
        return "PR 1"

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["parallelCommandsStart"]
