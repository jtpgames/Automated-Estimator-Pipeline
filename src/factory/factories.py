from typing import Any

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectFromModel, SelectKBest, SelectPercentile
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from src.logfile_etl.log_converter.ars_logfile_converter import ARSLogConverter
from src.logfile_etl.log_converter.locust_logfile_converter import LocustLogfileConverter
from src.logfile_etl.log_converter.ws_logfile_converter import WSLogConverter
from src.feature_extractor.arrive_time_extractor import ArriveTimeAnalysisExtractor, \
    ArriveTimeETLExtractor
from src.feature_extractor.cmd_extractor import CMDETLExtractor, CMDAnalysisExtractor, CMDOneHotAnalysisExtractor, \
    CMDTargetEncodingAnalysisExtractor
from src.feature_extractor.first_parallel_request_finished_extractor import \
    FirstCommandEndAnalysisExtractor, FirstParallelRequestFinishedETLExtractor
from src.feature_extractor.first_parallel_request_start_extractor import \
    FirstCommandStartAnalysisExtractor, FirstParallelRequestStartETLExtractor
from src.feature_extractor.list_parallel_request_end_extractor import ListParallelRequestsEndAnalysisExtractor, \
    ListParallelRequestsEndETLExtractor, \
    HashListPR2TypesWithCountAnalysisExtractor
from src.feature_extractor.list_parallel_request_finished_extractor import \
    ListParallelRequestsFinishedAnalysisExtractor, \
    ListParallelRequestsFinishedETLExtractor, \
    HashListPR3TypesWithCountAnalysisExtractor
from src.feature_extractor.list_parallel_request_start_extractor import \
    ListParallelRequestsStartETLExtractor, \
    ListParallelRequestsStartAnalysisExtractor, \
    HashListPR1TypesWithCountAnalysisExtractor
from src.feature_extractor.number_parallel_requests_end_extractor import \
    ParallelRequestsTwoETLExtractor, PRTwoAnalysisExtractor
from src.feature_extractor.number_parallel_requests_finished_extractor import \
    PRThreeAnalysisExtractor, ParallelRequestsThreeETLExtractor
from src.feature_extractor.number_parallel_requests_start_extractor import \
    PROneAnalysisExtractor, ParallelRequestsOneETLExtractor
from src.feature_extractor.response_time_extractor import \
    ResponseTimeMilliSecAnalysisExtractor, ResponseTimeETLExtractor, ResponseTimeSecAnalysisExtractor
from src.feature_extractor.timestamp_extractor import TimestampETLExtractor


class ConverterFactory:
    __converter = {
        "WS": WSLogConverter,
        "ARS": ARSLogConverter,
        "LOCUST": LocustLogfileConverter
    }

    def get(self, name):
        converter = self.__converter.get(name)
        if not converter:
            raise ValueError(name)
        return converter


class EstimatorFactory:
    __estimators = {
        "LR": LinearRegression,
        "Ridge": Ridge,
        "Lasso": Lasso,
        "DT": DecisionTreeRegressor,
        "ElasticNet": ElasticNet,
        "RF": RandomForestRegressor,
        "SGDR": SGDRegressor
    }

    def get(self, name: str) -> Any:
        estimator = self.__estimators.get(name)
        if not estimator:
            raise ValueError(name)
        return estimator


class EstimatorPipelineActionFactory:
    __actions = {
        "std": StandardScaler,
        "pca": PCA,
        "select_from_model": SelectFromModel,
        "k_best": SelectKBest,
        "percentile": SelectPercentile
    }

    def get(self, name: str):
        action = self.__actions.get(name)
        if not action:
            raise ValueError(name)
        return action


class DatabaseFeatureExtractorFactory:
    __extractors = {
        'cmd': CMDAnalysisExtractor,
        'cmd_target_encoding': CMDTargetEncodingAnalysisExtractor,
        'cmd_one_hot': CMDOneHotAnalysisExtractor,
        'pr_1': PROneAnalysisExtractor,
        'pr_2': PRTwoAnalysisExtractor,
        'pr_3': PRThreeAnalysisExtractor,
        'response_time_milli': ResponseTimeMilliSecAnalysisExtractor,
        'response_time_sec': ResponseTimeSecAnalysisExtractor,
        'list_pr_3': ListParallelRequestsFinishedAnalysisExtractor,
        'list_pr_1': ListParallelRequestsStartAnalysisExtractor,
        'list_pr_2': ListParallelRequestsEndAnalysisExtractor,
        'hash_list_pr_3': HashListPR3TypesWithCountAnalysisExtractor,
        'hash_list_pr_1': HashListPR1TypesWithCountAnalysisExtractor,
        'hash_list_pr_2': HashListPR2TypesWithCountAnalysisExtractor,
        'arrive_interval': ArriveTimeAnalysisExtractor,
    }

    def get(self, name: str):
        extractor = self.__extractors.get(name)
        if not extractor:
            raise ValueError(name)
        return extractor


class LogfileFeatureExtractorFactory:
    __extractors = {
        'cmd': CMDETLExtractor,
        'pr_1': ParallelRequestsOneETLExtractor,
        'pr_2': ParallelRequestsTwoETLExtractor,
        'pr_3': ParallelRequestsThreeETLExtractor,
        'first_pr_1': FirstParallelRequestStartETLExtractor,
        'first_pr_3': FirstParallelRequestFinishedETLExtractor,
        'response_time': ResponseTimeETLExtractor,
        'list_pr_3': ListParallelRequestsFinishedETLExtractor,
        'list_pr_1': ListParallelRequestsStartETLExtractor,
        'list_pr_2': ListParallelRequestsEndETLExtractor,
        'arrive_interval': ArriveTimeETLExtractor,
        'arrive_timestamp': TimestampETLExtractor,
    }

    def get(self, name: str):
        extractor = self.__extractors.get(name)
        if not extractor:
            raise ValueError(name)
        return extractor
