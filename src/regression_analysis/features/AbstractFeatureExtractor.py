from abc import ABC, abstractmethod

import pandas as pd

from src.regression_analysis.CommandNumberMapping import mapping
from src.regression_analysis.Database import Database


class AbstractFeatureExtractor(ABC):
    @abstractmethod
    def get_column_name(self) -> str:
        pass

    @abstractmethod
    def get_df(self, db: Database, names_mapping) -> pd.DataFrame:
        pass

    def load_df_column_from_db(self, db) -> pd.DataFrame:
        return pd.read_sql_table(
            "gs_training_data", db.connection(), columns=[self.get_column_name()]
        )

    def get_cmd_int(self, cmd):
        if cmd not in mapping:
            mapping[cmd] = len(mapping) + 1

        return mapping[cmd]
