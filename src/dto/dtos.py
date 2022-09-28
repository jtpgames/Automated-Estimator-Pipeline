from dataclasses import field
from typing import Optional
from typing import Union

from marshmallow_dataclass import dataclass

from src.factory.factories import EstimatorFactory, EstimatorPipelineActionFactory


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

    def __set_pipeline_for_estimators(self):
        if len(self.pipelines) == 1:
            self.pipelines[0].for_estimators = [estimator.name for estimator in self.estimators]

    def get_params(self):
        all_step_names = []
        parameter_grid = []
        self.__set_pipeline_for_estimators()
        estimator_factory = EstimatorFactory()
        action_factory = EstimatorPipelineActionFactory()
        for estimator_config in self.estimators:
            estimator = estimator_factory.get(estimator_config.name)()
            params_to_rename = estimator_config.params
            params = {"estimator": [estimator]}

            for pipeline in self.pipelines:
                if estimator_config.name in pipeline.for_estimators:
                    for step in pipeline.steps:
                        # pipeline step name with prefix for compatible estimators e.g. dt_linear_scaler
                        step_prefix = "_".join(pipeline.for_estimators) + "_"
                        step_name = step_prefix + step.step

                        # add step name to all pipeline steps list if not already present
                        if step_name not in all_step_names:
                            all_step_names.append(step_name)

                        # initalize action with estimator as input if needed and add
                        # to the parameter grid of the estimator. e.g. dt_select_from_model: [SelectFromModel(estimator)]
                        action = action_factory.get(step.action)
                        if step.needs_estimator:
                            params[step_name] = [action(estimator)]
                        else:
                            params[step_name] = [action()]

                        # add all remaining grid params with pipeline
                        for key, value in step.params.items():
                            params[step_name + "__" + key] = value

            for key, value in params_to_rename.items():
                params["estimator__" + key] = value

            parameter_grid.append(params)

        # add estimator as last pipeline step
        all_step_names.append("estimator")
        # all pipeline steps
        all_pipeline_steps = []
        for step in all_step_names:
            all_pipeline_steps.append((step, "passthrough"))

        return {"steps": all_pipeline_steps, "parameter_grid": parameter_grid,
                "grid_search_params": GridSearch.Schema().dump(self.grid_search),
                "cv_params": CrossValidation.Schema().dump(self.cross_validation)}

    def __initialize_estimators(self):
        pass

    def __initalize_actions(self):
        pass

    def get_grid_search_parameter(self):
        # if multiple scoring metrices are defined, refit has to be set
        if self.grid_search.refit is not None:
            return {
                "key": "rank_test_" + self.grid_search.refit,
                "values": ["mean_test_" + x for x in self.grid_search.scoring],
                "names": self.grid_search.scoring
            }
        else:
            # if refit is not set, then scoring has to be a single value
            return {"key": "rank_test_score", "values": ["mean_test_score"],
                    "names": [self.grid_search.scoring]}

    def uses_feature_selector(self):
        pipeline_steps = [step.step for pipeline in self.pipelines for step in pipeline.steps]
        print("feature_selection" in pipeline_steps)
        return "feature_selection" in pipeline_steps


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
