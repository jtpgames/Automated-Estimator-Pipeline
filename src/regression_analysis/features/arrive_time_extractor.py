import pandas as pd
from numpy import short

from src.regression_analysis.configuration_handler import ConfigurationHandler
from src.regression_analysis.database import Database
from src.regression_analysis.features.abstract_feature_extractor import \
    AbstractFeatureExtractor
from src.regression_analysis.features.list_parallel_command_finished_extractor import \
    ListParallelRequestsFinished


class ArriveTimeExtractor(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "arrive time"

    def get_df(self, db, names_mapping) -> pd.DataFrame:
        return self.load_df_column_from_db(db).astype(short, copy=False)
