import numpy as np
import pandas as pd

from configuration import Configuration
from database import Database
from feature_extractor.cmd_extractor import CMDAnalysisExtractor


class OutlierDetection:
    def __init__(self, config: Configuration, database: Database):
        self.__config_handler = config
        self.__db = database

    # TODO vernünftig machen
    def remove_outliers_inplace(self, df: pd.DataFrame) -> pd.DataFrame:
        if "CMD" == self.__config_handler.get_outlier_detection_type():
            delete_cmd_after = False
            if "cmd" not in df.columns.values:
                extractor = CMDAnalysisExtractor(self.__db, "cmd")
                new_df = extractor.get_df()
                df = pd.merge(
                    df,
                    new_df,
                    how="inner",
                    left_index=True,
                    right_index=True
                )
                delete_cmd_after = True
            df = df[
                ~df.groupby("cmd")[self.__config_handler.get_y_column_name()].apply(self.__is_outlier)]
            if delete_cmd_after:
                df.drop("cmd", axis=1, inplace=True)
        else:
            df = df[
                np.abs(
                    df[self.__config_handler.get_y_column_name()] - df[
                        self.__config_handler.get_y_column_name()].mean()
                ) <= (
                        self.__config_handler.get_outlier_std_threshold() * df[
                    self.__config_handler.get_y_column_name()].std())]
        return df

    @staticmethod
    def __is_outlier(s):
        lower_limit = s.mean() - (s.std() * 3)
        upper_limit = s.mean() + (s.std() * 3)
        return ~s.between(lower_limit, upper_limit)
