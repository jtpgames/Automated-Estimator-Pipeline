from sqlalchemy import Column, Integer

from src.regression_analysis.features.abstract_feature_extractor import \
    AbstractFeatureExtractor


class ArriveTimeExtractor(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "arrive time"

    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)
