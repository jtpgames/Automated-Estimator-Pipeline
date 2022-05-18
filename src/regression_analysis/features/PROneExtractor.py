from numpy import short

from src.regression_analysis.Database import Database
from src.regression_analysis.features.AbstractFeatureExtractor import (
    AbstractFeatureExtractor,
)

import pandas as pd


class PROneExtractor(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "PR 1"

    def get_df(self, db: Database, names_mapping) -> pd.DataFrame:
        return self.load_df_column_from_db(db).astype(short, copy=False)
