from src.regression_analysis.database import Database
from src.regression_analysis.features.arrive_time_extractor import \
    ArriveTimeExtractor
from src.regression_analysis.features.cmd_extractor import CMDExtractor
from src.regression_analysis.features.abstract_feature_extractor import \
    AbstractFeatureExtractor
from src.regression_analysis.features.first_parallel_command_finished_extractor import \
    FirstCommandEndExtractor
from src.regression_analysis.features.first_parallel_commands_start_extractor import \
    FirstCommandStartExtractor
from src.regression_analysis.features.list_parallel_command_finished_extractor import \
    ListParallelRequestsFinished
from src.regression_analysis.features.list_parallel_command_start_extractor import \
    ListParallelRequestsStart
from src.regression_analysis.features.number_parallel_requests_finished_extractor import \
    PRThreeExtractor
from src.regression_analysis.features.number_parallel_requests_start_extractor import \
    PROneExtractor
from src.regression_analysis.features.response_time_extractor import \
    ResponseTimeExtractor
from typing import Dict, List

func_calls_dict: Dict[str, AbstractFeatureExtractor] = {
    'cmd': CMDExtractor,
    'PR 1': PROneExtractor,
    'PR 3': PRThreeExtractor,
    'First Command Start': FirstCommandStartExtractor,
    'First Command Finished': FirstCommandEndExtractor,
    'response time': ResponseTimeExtractor,
    'List parallel requests finished': ListParallelRequestsFinished,
    'List parallel requests start': ListParallelRequestsStart,
    'arrive time': ArriveTimeExtractor,
}

def get_feature_extractors_by_name(db:Database, feature_extractor_names: List[str]) -> List[AbstractFeatureExtractor]:
    feature_extractors = []
    for extractors_name in feature_extractor_names:
        feature_extractors.append(func_calls_dict[extractors_name](db, extractors_name))
    return feature_extractors
