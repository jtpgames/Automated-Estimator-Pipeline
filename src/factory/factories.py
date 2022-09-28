from typing import Any

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectFromModel, SelectKBest, SelectPercentile
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from src.feature_extractor.arrive_time_extractor import ArriveTimeAnalysisExtractor, \
    ArriveTimeETLExtractor
from src.feature_extractor.cmd_extractor import CMDETLExtractor, CMDAnalysisExtractor, CMDOneHotAnalysisExtractor
from src.feature_extractor.first_parallel_request_finished_extractor import \
    FirstCommandEndAnalysisExtractor, FirstParallelRequestFinishedETLExtractor
from src.feature_extractor.first_parallel_request_start_extractor import \
    FirstCommandStartAnalysisExtractor, FirstParallelRequestStartETLExtractor
from src.feature_extractor.list_parallel_request_end_extractor import ListParallelRequestsEndAnalysisExtractor, \
    ListParallelRequestsEndETLExtractor
from src.feature_extractor.list_parallel_request_finished_extractor import \
    ListParallelRequestsFinishedAnalysisExtractor, \
    ListParallelRequestsFinishedETLExtractor
from src.feature_extractor.list_parallel_request_start_extractor import \
    ListParallelRequestsStartETLExtractor, \
    ListParallelRequestsStartAnalysisExtractor
from src.feature_extractor.number_parallel_requests_end_extractor import \
    ParallelRequestsTwoETLExtractor, PRTwoAnalysisExtractor
from src.feature_extractor.number_parallel_requests_finished_extractor import \
    PRThreeAnalysisExtractor, ParallelRequestsThreeETLExtractor
from src.feature_extractor.number_parallel_requests_start_extractor import \
    PROneAnalysisExtractor, ParallelRequestsOneETLExtractor
from src.feature_extractor.response_time_extractor import \
    ResponseTimeAnalysisExtractor, ResponseTimeETLExtractor
from src.feature_extractor.timestamp_extractor import TimestampETLExtractor


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
        'cmd one hot': CMDOneHotAnalysisExtractor,
        'PR 1': PROneAnalysisExtractor,
        'PR 2': PRTwoAnalysisExtractor,
        'PR 3': PRThreeAnalysisExtractor,
        'First Command Start': FirstCommandStartAnalysisExtractor,
        'First Command Finished': FirstCommandEndAnalysisExtractor,
        'response time': ResponseTimeAnalysisExtractor,
        'List parallel requests finished': ListParallelRequestsFinishedAnalysisExtractor,
        'List parallel requests start': ListParallelRequestsStartAnalysisExtractor,
        'List parallel requests end': ListParallelRequestsEndAnalysisExtractor,
        'arrive time': ArriveTimeAnalysisExtractor,
    }

    def get(self, name: str):
        extractor = self.__extractors.get(name)
        if not extractor:
            raise ValueError(name)
        return extractor


class LogfileFeatureExtractorFactory:
    __extractors = {
        'cmd': CMDETLExtractor,
        'PR 1': ParallelRequestsOneETLExtractor,
        'PR 2': ParallelRequestsTwoETLExtractor,
        'PR 3': ParallelRequestsThreeETLExtractor,
        'First Command Start': FirstParallelRequestStartETLExtractor,
        'First Command Finished': FirstParallelRequestFinishedETLExtractor,
        'response time': ResponseTimeETLExtractor,
        'List parallel requests finished': ListParallelRequestsFinishedETLExtractor,
        'List parallel requests start': ListParallelRequestsStartETLExtractor,
        'List parallel requests end': ListParallelRequestsEndETLExtractor,
        'arrive time': ArriveTimeETLExtractor,
        'Timestamp': TimestampETLExtractor,
    }

    def get(self, name: str):
        extractor = self.__extractors.get(name)
        if not extractor:
            raise ValueError(name)
        return extractor
