import logging
from typing import List

from src.logfile_etl.feature_extractor.abstract_feature_extractor import (
    AbstractFeatureETLExtractor,
)
from src.logfile_etl.feature_extractor.arrive_time_extractor import \
    ArriveTimeETLExtractor
from src.logfile_etl.feature_extractor.cmd_extractor import CMDETLExtractor
from src.logfile_etl.feature_extractor.first_parallel_request_finished_extractor import (
    FirstParallelRequestFinishedETLExtractor,
)
from src.logfile_etl.feature_extractor.fist_parallel_request_start_extractor import (
    FirstParallelRequestStartETLExtractor,
)
from src.logfile_etl.feature_extractor.list_parallel_requests_finished import ListParallelRequestsFinishedETLExtractor
from src.logfile_etl.feature_extractor.list_parallel_requests_start import ListParallelRequestsStartETLExtractor
from src.logfile_etl.feature_extractor.number_parallel_requests_start_extractor import (
    ParallelRequestsOneETLExtractor,
)
from src.logfile_etl.feature_extractor.number_parallel_requests_finished_extractor import (
    ParallelRequestsThreeETLExtractor,
)
from src.logfile_etl.feature_extractor.number_parallel_requests_end_extractor import (
    ParallelRequestsTwoETLExtractor,
)
from src.logfile_etl.feature_extractor.response_time_extractor import (
    ResponseTimeETLExtractor,
)
from src.logfile_etl.feature_extractor.timestamp_extractor import TimestampETLExtractor

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


def get_feature_extractors_from_names(
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
