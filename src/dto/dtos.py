from dataclasses import field
from typing import Optional
from typing import Union

from marshmallow_dataclass import dataclass


@dataclass
class GridSearchDTO:
    scoring: Union[str, list[str]]
    refit: Optional[str]
    verbose: Optional[int] = 1
    n_jobs: Optional[int] = None
    pre_dispatch: Union[Optional[int], Optional[str]] = "2*n_jobs"


@dataclass
class EstimatorDTO:
    name: str
    params: dict


@dataclass
class PipelineStepDTO:
    step: str
    action: str
    params: dict
    needs_estimator: Optional[bool] = False


@dataclass
class PipelineDTO:
    for_estimators: Optional[list[str]] = field(default_factory=list)
    steps: list[PipelineStepDTO] = field(default_factory=list)


@dataclass
class CrossValidationDTO:
    n_splits: Optional[int] = 5
    shuffle: Optional[bool] = True
    random_state: Optional[int] = 42


@dataclass
class GridSearchWrapperDTO:
    pipelines: list[PipelineDTO]
    grid_search: GridSearchDTO
    estimators: list[EstimatorDTO]
    cross_validation: Optional[CrossValidationDTO]
    export_folder: str


@dataclass
class LogfileETLPipelineDTO:
    unprocessed_logfiles_folder: str
    processed_logfiles_folder: str
    extractors: list[str]
    force: bool
    converter: list[str]


@dataclass
class WorkloadCharacterizationDTO:
    export_folder: str


@dataclass
class EstimatorPipelineDTO:
    features: list[str]
    y_column: str
    grid_search_wrapper: GridSearchWrapperDTO


@dataclass
class OutlierDetectionDTO:
    remove_outlier: bool = True
    outlier_modus: str = "CMD"  # possible values : "CMD" and "Y"
    std_threshold: int = 3


@dataclass
class DatabaseDTO:
    name: str
    folder: str
    row_limit: int = -1


@dataclass
class ConfigFile:
    outlier_detection: OutlierDetectionDTO
    database: DatabaseDTO
    estimator_pipe: EstimatorPipelineDTO
    logfile_etl_pipe: LogfileETLPipelineDTO
    workload: WorkloadCharacterizationDTO
