import logging
from typing import List

import pandas as pd

from database import Database
from factory.factories import DatabaseFeatureExtractorFactory


class DataPreparation:

    def __init__(self, feature_names: List[str], database: Database):
        self.__feature_names = feature_names
        self.__db = database

    def get_feature_df(self):
        feature_extractors = self.__setup_feature_extractors()
        return self.__load_data(feature_extractors)

    def __setup_feature_extractors(self) -> List:
        factory = DatabaseFeatureExtractorFactory()
        extractors = []
        for name in self.__feature_names:
            extractor_class = factory.get(name)
            extractor_object = extractor_class(self.__db, name)
            extractors.append(extractor_object)
        return extractors

    @staticmethod
    def __load_data(extractors) -> pd.DataFrame:
        df = pd.DataFrame()
        for extractor in extractors:
            if df.empty:
                df = extractor.get_df()
            else:
                new_df = extractor.get_df()
                df = pd.merge(
                    df,
                    new_df,
                    how="inner",
                    left_index=True,
                    right_index=True
                )

            logging.info(df.shape)
        return df
