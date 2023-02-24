import category_encoders as ce
import pandas as pd
from sqlalchemy import Column, Integer

from src.feature_extractor.encoder.seconds_encoder import MilliSecondsEncoder
from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractETLFeatureExtractor
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class CMDAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)


class CMDOneHotAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column("cmd", Integer)

    def get_df(self) -> pd.DataFrame:
        result_data = self.get_column_data(self.get_column())
        df = self.get_df_from_db_column_data(result_data)
        data = pd.get_dummies(df, prefix=['cmd'], columns=[self.get_column_name()], drop_first=True)
        return data


class CMDTargetEncodingAnalysisExtractor(AbstractAnalysisFeatureExtractor):
    def get_column(self) -> Column:
        return Column("cmd", Integer)

    def get_df(self) -> pd.DataFrame:
        response_time_column = Column("response_time", MilliSecondsEncoder)
        result_data = self.db.get_training_data_cursor_result_columns(
            [self.get_column(), response_time_column]).all()
        df = pd.DataFrame.from_records(
            result_data,
            index='index',
            columns=['index', self.get_column_name(), "response_time"]
        )
        encoder = ce.TargetEncoder(cols=[self.get_column_name()])
        df[self.get_column_name()] = encoder.fit_transform(df[self.get_column_name()], df["response_time"])
        df.drop("response_time", axis=1, inplace=True)
        return df


class CMDETLExtractor(AbstractETLFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_feature_name(), Integer)

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["cmd"]
