import logging
from typing import List

from src.logfile_etl.feature_extractor.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)
from src.logfile_etl.feature_extractor.cmd_extractor import CMDExtractor
from src.logfile_etl.feature_extractor.first_parallel_request_finished_extractor import (
    FirstParallelRequestFinishedExtractor,
)
from src.logfile_etl.feature_extractor.fist_parallel_request_start_extractor import (
    FirstParallelRequestStartExtractor,
)
from src.logfile_etl.feature_extractor.number_parallel_requests_start_extractor import (
    ParallelRequestsOne,
)
from src.logfile_etl.feature_extractor.number_parallel_requests_finished_extractor import (
    ParallelRequestsThree,
)
from src.logfile_etl.feature_extractor.number_parallel_requests_end_extractor import (
    ParallelRequestsTwo,
)
from src.logfile_etl.feature_extractor.response_time_extractor import (
    ResponseTimeExtractor,
)
from src.logfile_etl.feature_extractor.timestamp_extractor import TimestampExtractor

possible_feature_extractors: List[AbstractFeatureExtractor] = [
    ParallelRequestsOne(),
    ParallelRequestsTwo(),
    ParallelRequestsThree(),
    ResponseTimeExtractor(),
    CMDExtractor(),
    TimestampExtractor(),
    FirstParallelRequestStartExtractor(),
    FirstParallelRequestFinishedExtractor(),
]


def get_feature_extractors_from_names(
    extractor_names: List[str],
) -> List[AbstractFeatureExtractor]:
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
