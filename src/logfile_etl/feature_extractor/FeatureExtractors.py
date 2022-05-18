import logging
from typing import List

from src.logfile_etl.feature_extractor.AbstractFeatureExtractor import (
    AbstractFeatureExtractor,
)
from src.logfile_etl.feature_extractor.Cmd import Cmd
from src.logfile_etl.feature_extractor.FirstParallelRequestFinished import (
    FirstParallelRequestFinished,
)
from src.logfile_etl.feature_extractor.FirstParallelRequestStart import (
    FirstParallelRequestStart,
)
from src.logfile_etl.feature_extractor.ParallelRequestsOne import ParallelRequestsOne
from src.logfile_etl.feature_extractor.ParallelRequestsThree import (
    ParallelRequestsThree,
)
from src.logfile_etl.feature_extractor.ParallelRequestsTwo import ParallelRequestsTwo
from src.logfile_etl.feature_extractor.ReponseTime import ResponseTime
from src.logfile_etl.feature_extractor.Timestamp import Timestamp

possible_feature_extractors: List[AbstractFeatureExtractor] = [
    ParallelRequestsOne(),
    ParallelRequestsTwo(),
    ParallelRequestsThree(),
    ResponseTime(),
    Cmd(),
    Timestamp(),
    FirstParallelRequestStart(),
    FirstParallelRequestFinished(),
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
