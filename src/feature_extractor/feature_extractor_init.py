import logging
from typing import Dict, List

from src.feature_extractor.abstract_feature_extractor import AbstractAnalysisFeatureExtractor, \
    AbstractFeatureETLExtractor
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


possible_feature_extractors: List[AbstractFeatureETLExtractor] = [
    ParallelRequestsOneETLExtractor(),
    ParallelRequestsTwoETLExtractor(),
    ParallelRequestsThreeETLExtractor(),
    ResponseTimeETLExtractor(),
    CMDETLExtractor(),
    TimestampETLExtractor(),
    FirstParallelRequestStartETLExtractor(),
    FirstParallelRequestFinishedETLExtractor(),
    ListParallelRequestsStartETLExtractor(),
    ListParallelRequestsFinishedETLExtractor(),
    ArriveTimeETLExtractor()
]


def get_feature_extractors_by_name_etl(
        extractor_names: List[str],
) -> List[AbstractFeatureETLExtractor]:
    feature_extractors = []
    for extractor in extractor_names:
        extractor_found = False
        for actual_extractor in possible_feature_extractors:
            if extractor == actual_extractor.get_feature_name():
                feature_extractors.append(actual_extractor)
                extractor_found = True
        if not extractor_found:
            logging.warning("No feature extractor found for name: ", extractor)
    return feature_extractors
