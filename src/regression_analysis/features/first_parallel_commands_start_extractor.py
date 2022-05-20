from numpy import short

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)
import pandas as pd


class FirstCommandStartExtractor(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "First Command Start"

    def get_df(self, db, names_mapping) -> pd.DataFrame:
        df = self.load_df_column_from_db(db)
        return (
            df[self.get_column_name()]
            .apply(self.__apply_func, args=(names_mapping,))
            .astype(short, copy=False)
        )

    def __apply_func(self, cmd, names_mapping):
        if cmd is not None:
            return self.get_cmd_int(cmd, names_mapping)
        else:
            return 0
