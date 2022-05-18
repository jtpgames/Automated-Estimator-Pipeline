from typing import List

from src.regression_analysis.features.AbstractFeatureExtractor import (
    AbstractFeatureExtractor,
)
from src.regression_analysis.features.CMDExtractor import CMDExtractor
from src.regression_analysis.features.FirstCommandEndExtractor import (
    FirstCommandEndExtractor,
)
from src.regression_analysis.features.FirstCommandStartExtractor import (
    FirstCommandStartExtractor,
)
from src.regression_analysis.features.PROneExtractor import PROneExtractor
from src.regression_analysis.features.PRThreeExtractor import PRThreeExtractor
from src.regression_analysis.features.ResponseTimeExtractor import ResponseTimeExtractor

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
