from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractETLFeatureExtractor, AbstractAnalysisFeatureExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class PRTwoAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)


class ParallelRequestsTwoETLExtractor(AbstractETLFeatureExtractor):

    def get_column(self) -> Column:
        return Column(self.get_feature_name(), Integer)

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["parallelCommandsEnd"]
