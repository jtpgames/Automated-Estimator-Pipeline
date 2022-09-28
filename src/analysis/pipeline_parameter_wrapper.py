from configuration import Configuration
from dto.dtos import GridSearch, CrossValidation
from factory.factories import EstimatorFactory, EstimatorPipelineActionFactory


class PipelineParameterWrapper:

    def __init__(self, config: Configuration):
        self.__estimator_handler = config.get_estimator_handler()
        self.__estimator_factory = EstimatorFactory()
        self.__action_factory = EstimatorPipelineActionFactory()

    def __set_pipeline_for_estimators(self):
        if len(self.__estimator_handler.pipelines) == 1:
            self.__estimator_handler.pipelines[0].for_estimators = [estimator.name for estimator in
                                                                    self.__estimator_handler.estimators]

    def get_params(self):
        all_step_names = []
        parameter_grid = []
        self.__set_pipeline_for_estimators()
        for estimator_config in self.__estimator_handler.estimators:
            estimator = self.__estimator_factory.get(estimator_config.name)()
            params_to_rename = estimator_config.params
            params = {"estimator": [estimator]}

            for pipeline in self.__estimator_handler.pipelines:
                if estimator_config.name in pipeline.for_estimators:
                    for step in pipeline.steps:
                        self.build_step(all_step_names, estimator, params, pipeline, step)

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
                "grid_search_params": GridSearch.Schema().dump(self.__estimator_handler.grid_search),
                "cv_params": CrossValidation.Schema().dump(self.__estimator_handler.cross_validation)}

    def build_step(self, all_step_names, estimator, params, pipeline, step):
        # pipeline step name with prefix for compatible estimators e.g. dt_linear_scaler
        step_prefix = "_".join(pipeline.for_estimators) + "_"
        step_name = step_prefix + step.step
        # add step name to all pipeline steps list if not already present
        if step_name not in all_step_names:
            all_step_names.append(step_name)
        # initalize action with estimator as input if needed and add
        # to the parameter grid of the estimator. e.g. dt_select_from_model: [SelectFromModel(estimator)]
        action = self.__action_factory.get(step.action)
        if step.needs_estimator:
            params[step_name] = [action(estimator)]
        else:
            params[step_name] = [action()]
        # add all remaining grid params with pipeline
        for key, value in step.params.items():
            params[step_name + "__" + key] = value

    def get_grid_search_parameter(self):
        # if multiple scoring metrices are defined, refit has to be set
        if self.__estimator_handler.grid_search.refit is not None:
            return {
                "key": "rank_test_" + self.__estimator_handler.grid_search.refit,
                "values": ["mean_test_" + x for x in self.__estimator_handler.grid_search.scoring],
                "names": self.__estimator_handler.grid_search.scoring
            }
        else:
            # if refit is not set, then scoring has to be a single value
            return {"key": "rank_test_score", "values": ["mean_test_score"],
                    "names": [self.__estimator_handler.grid_search.scoring]}

    def uses_feature_selector(self):
        pipeline_steps = [step.step for pipeline in self.__estimator_handler.pipelines for step in pipeline.steps]
        print("feature_selection" in pipeline_steps)
        return "feature_selection" in pipeline_steps
