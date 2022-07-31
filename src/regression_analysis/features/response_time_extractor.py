from sqlalchemy import Column, Integer

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)


class ResponseTimeExtractor(AbstractFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)
