from dataclasses import field
from typing import Optional
from typing import Union

from marshmallow_dataclass import dataclass


@dataclass
class GridSearch:
    scoring: Union[str, list[str]]
    refit: Optional[str]
    verbose: Optional[int] = 1
    n_jobs: Optional[int] = None
    pre_dispatch: Union[Optional[int], Optional[str]] = "2*n_jobs"


@dataclass
class Estimator:
    name: str
    params: dict


@dataclass
class PipelineStep:
    step: str
    action: str
    params: dict
    needs_estimator: Optional[bool] = False


@dataclass
class Pipeline:
    for_estimators: Optional[list[str]] = field(default_factory=list)
    steps: list[PipelineStep] = field(default_factory=list)


@dataclass
class CrossValidation:
    n_splits: Optional[int] = 5
    shuffle: Optional[bool] = True
    random_state: Optional[int] = 42


@dataclass
class EstimatorHandler:
    pipelines: list[Pipeline]
    grid_search: GridSearch
    estimators: list[Estimator]
    cross_validation: Optional[CrossValidation]


@dataclass
class LogfileExtractorConfig:
    unprocessed_logfiles: str
    processed_logfiles: str
    extractors: list[str]
    force: bool


@dataclass
class WorkloadCharacterizationConfig:
    export_folder: str
    remove_response_time_outliers: bool = True


@dataclass
class AnalysisConfig:
    features: list[str]
    y: str
    estimator_handler: EstimatorHandler
    model_save_path: str
    outlier_detection_based_on_cmd_type: bool


@dataclass
class Database:
    name: str
    folder: str
    limit: int = -1


@dataclass
class ConfigFile:
    database: Database
    analysis: AnalysisConfig
    logfile: LogfileExtractorConfig
    workload: WorkloadCharacterizationConfig
