from numpy import short
from sqlalchemy import Column, Integer

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor, trainings_data_table_name
)
import pandas as pd


class CMDExtractor(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "cmd"

    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)
