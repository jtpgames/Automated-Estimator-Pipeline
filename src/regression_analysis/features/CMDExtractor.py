from numpy import short

from src.regression_analysis.features.AbstractFeatureExtractor import (
    AbstractFeatureExtractor,
)
import pandas as pd


class CMDExtractor(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "cmd"

    def get_df(self, db, names_mapping) -> pd.DataFrame:
        df = self.load_df_column_from_db(db)
        return (
            df[self.get_column_name()].apply(self.get_cmd_int).astype(short, copy=False)
        )
