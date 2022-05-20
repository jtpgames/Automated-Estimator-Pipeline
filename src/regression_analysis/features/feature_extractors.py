from typing import List

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)
from src.regression_analysis.features.cmd_extractor import CMDExtractor
from src.regression_analysis.features.first_parallel_command_finished_extractor import (
    FirstCommandEndExtractor,
)
from src.regression_analysis.features.first_parallel_commands_start_extractor import (
    FirstCommandStartExtractor,
)
from src.regression_analysis.features.number_parallel_requests_start_extractor import (
    PROneExtractor,
)
from src.regression_analysis.features.number_parallel_requests_finished_extractor import (
    PRThreeExtractor,
)
from src.regression_analysis.features.response_time_extractor import (
    ResponseTimeExtractor,
)

# TODO dict with refrence on init method. so only actually used extractors get initialized
possible_extractors: List[AbstractFeatureExtractor] = [
    CMDExtractor(),
    PROneExtractor(),
    PRThreeExtractor(),
    FirstCommandStartExtractor(),
    FirstCommandEndExtractor(),
    ResponseTimeExtractor(),
]


def get_feature_extractors_by_name(
    extractor_names: List[str],
) -> List[AbstractFeatureExtractor]:
    feature_extractors = []
    for extractor_name in extractor_names:
        for poss_extractor in possible_extractors:
            if extractor_name == poss_extractor.get_column_name():
                feature_extractors.append(poss_extractor)
    return feature_extractors
