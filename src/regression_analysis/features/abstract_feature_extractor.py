from abc import ABC, abstractmethod

import pandas as pd

from src.regression_analysis.database import Database


class AbstractFeatureExtractor(ABC):
    @abstractmethod
    def get_column_name(self) -> str:
        pass

    @abstractmethod
    def get_df(self, db: Database, names_mapping) -> pd.DataFrame:
        pass

    def load_df_column_from_db(self, db) -> pd.DataFrame:
        # gs_training_data name of the training table
        return pd.read_sql_table(
            "test_table", db.connection(), columns=[self.get_column_name()]
        )

    def get_cmd_int(self, cmd, names_mapping):
        if cmd not in names_mapping:
            names_mapping[cmd] = len(names_mapping) + 1

        return names_mapping[cmd]
