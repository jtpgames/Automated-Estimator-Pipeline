from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractETLFeatureExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class FirstCommandStartAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)


class FirstParallelRequestStartETLExtractor(AbstractETLFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_feature_name(), Integer)

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["firstParallelCommandStart"]
