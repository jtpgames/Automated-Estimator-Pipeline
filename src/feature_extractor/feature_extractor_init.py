import logging
from typing import Dict, List

from src.feature_extractor.abstract_feature_extractor import AbstractAnalysisFeatureExtractor, \
    AbstractETLFeatureExtractor
from src.feature_extractor.cmd_extractor import CMDETLExtractor, CMDAnalysisExtractor
from src.database import Database
from src.feature_extractor.arrive_time_extractor import ArriveTimeAnalysisExtractor, \
    ArriveTimeETLExtractor
from src.feature_extractor.first_parallel_command_finished_extractor import \
    FirstCommandEndAnalysisExtractor, FirstParallelRequestFinishedETLExtractor
from src.feature_extractor.first_parallel_commands_start_extractor import \
    FirstCommandStartAnalysisExtractor, FirstParallelRequestStartETLExtractor
from src.feature_extractor.list_parallel_command_finished_extractor import \
    ListParallelRequestsFinishedAnalysisExtractor, \
    ListParallelRequestsFinishedETLExtractor
from src.feature_extractor.list_parallel_command_start_extractor import \
    ListParallelRequestsStartETLExtractor, \
    ListParallelRequestsStartAnalysisExtractor
from src.feature_extractor.number_parallel_requests_end_extractor import \
    ParallelRequestsTwoETLExtractor
from src.feature_extractor.number_parallel_requests_finished_extractor import \
    PRThreeAnalysisExtractor, ParallelRequestsThreeETLExtractor
from src.feature_extractor.number_parallel_requests_start_extractor import \
    PROneAnalysisExtractor, ParallelRequestsOneETLExtractor
from src.feature_extractor.response_time_extractor import \
    ResponseTimeAnalysisExtractor, ResponseTimeETLExtractor
from src.feature_extractor.timestamp_extractor import TimestampETLExtractor

analysis_extractor_generator_dict: Dict[
    str, AbstractAnalysisFeatureExtractor] = {
    'cmd': CMDAnalysisExtractor,
    'PR 1': PROneAnalysisExtractor,
    'PR 3': PRThreeAnalysisExtractor,
    'First Command Start': FirstCommandStartAnalysisExtractor,
    'First Command Finished': FirstCommandEndAnalysisExtractor,
    'response time': ResponseTimeAnalysisExtractor,
    'List parallel requests finished': ListParallelRequestsFinishedAnalysisExtractor,
    'List parallel requests start': ListParallelRequestsStartAnalysisExtractor,
    'arrive time': ArriveTimeAnalysisExtractor,
}

etl_extractor_generator_dict: Dict[
    str, AbstractETLFeatureExtractor] = {
    'cmd': CMDETLExtractor,
    'PR 1': ParallelRequestsOneETLExtractor,
    'PR 2': ParallelRequestsTwoETLExtractor,
    'PR 3': ParallelRequestsThreeETLExtractor,
    'First Command Start': FirstParallelRequestStartETLExtractor,
    'First Command Finished': FirstParallelRequestFinishedETLExtractor,
    'response time': ResponseTimeETLExtractor,
    'List parallel requests finished': ListParallelRequestsFinishedETLExtractor,
    'List parallel requests start': ListParallelRequestsStartETLExtractor,
    'arrive time': ArriveTimeETLExtractor,
    'Timestamp': TimestampETLExtractor,
}


def get_feature_extractors_by_name_analysis(
        db: Database,
        feature_extractor_names: List[str]
) -> List[AbstractAnalysisFeatureExtractor]:
    feature_extractors = []
    for extractors_name in feature_extractor_names:
        feature_extractors.append(
            analysis_extractor_generator_dict[extractors_name](
                db,
                extractors_name
            )
        )
    return feature_extractors


def get_feature_extractors_by_name_etl(
        feature_extractor_names: List[str]
) -> List[AbstractAnalysisFeatureExtractor]:
    feature_extractors = []
    for extractors_name in feature_extractor_names:
        feature_extractors.append(etl_extractor_generator_dict[extractors_name](
                extractors_name
            )
        )
    return feature_extractors
