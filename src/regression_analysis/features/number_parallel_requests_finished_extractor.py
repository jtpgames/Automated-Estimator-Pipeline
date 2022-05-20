from numpy import short

from src.regression_analysis.database import Database
from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)
import pandas as pd


class PRThreeExtractor(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "PR 3"

    def get_df(self, db: Database, names_mapping) -> pd.DataFrame:
        return self.load_df_column_from_db(db).astype(short, copy=False)
