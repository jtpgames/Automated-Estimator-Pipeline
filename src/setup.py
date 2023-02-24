import json
import os
import pathlib
from datetime import datetime

if __name__ == "__main__":
    parent_dir = pathlib.Path().absolute().parent
    resource_folder = parent_dir / "resources"
    unprocessed_folder = resource_folder / "logfiles" / "unprocessed"
    processed_folder = resource_folder / "logfiles" / "processed"
    export_folder = resource_folder / "export"
    db_folder = export_folder / "db"
    csv_folder = export_folder / "csv"
    statistics_folder = export_folder / "statistics"
    today = datetime.now().strftime("%Y-%m-%d")
    file_name = "trainingdata_{}.db".format(today)
    db_file = db_folder / file_name
    model_folder = resource_folder / "models"

    config_file = {
        "database": {
            "row_limit": -1,
            "name": "NEWEST",
            "folder": db_folder.as_posix()
        },
        "outlier_detection": {
            "remove_outlier": True,
            "outlier_modus": "CMD",
            "std_threshold": 3
        },
        "estimator_pipe": {
            "features": [
                "cmd_target_encoding",
                "pr_1",
                "response_time_sec"
            ],
            "y_column": "response_time_sec",
            "grid_search_wrapper": {
                "pipelines": [
                    {
                        "steps": [{
                            "step": "std",
                            "action": "std",
                            "params": {}
                        }],
                    }
                ],
                "estimators": [
                    {
                        "name": "LR",
                        "params": {}
                    },
                    {
                        "name": "DT",
                        "params": {
                            "criterion": ["squared_error", "friedman_mse", "absolute_error", "poisson"],
                            "max_depth": [2,4,6,8,10,12],
                            "min_samples_split": [2,4,6,8,10,12],
                            "min_samples_leaf": [1,2,3,4,5]
                        }
                    }
                ],
                "grid_search": {
                    "scoring": [
                        "r2",
                        "neg_mean_squared_error",
                        "neg_root_mean_squared_error"
                    ],
                    "refit": "r2",
                    "verbose": 2,
                    "pre_dispatch": "2*n_jobs",
                    "n_jobs": 4
                },
                "cross_validation": {
                    "n_splits": 10,
                    "shuffle": True,
                    "random_state": 42
                },
                "export_folder": export_folder.as_posix()
            }
        },
        "logfile_etl_pipe": {
            "unprocessed_logfiles_folder": unprocessed_folder.as_posix(),
            "processed_logfiles_folder": processed_folder.as_posix(),
            "extractors": [
                "cmd",
                "pr_1",
                "pr_2",
                "pr_3",
                "response_time",
                "list_pr_3",
                "list_pr_1",
                "list_pr_2",
                "arrive_interval",
                "arrive_timestamp"
            ],
            "force": True,
            "converter": [
                "ARS",
                "WS"
            ]
        },
        "workload": {
            "export_folder": statistics_folder.as_posix()
        }
    }

    configuration_folder = resource_folder / "config"

    user_config_file_path = configuration_folder / "config.json"

    os.makedirs(configuration_folder.as_posix(), exist_ok=True)

    with open(user_config_file_path, 'w+') as fp:
        json.dump(config_file, fp)

    print("Configuration files created in: {}".format(configuration_folder))

    os.makedirs(unprocessed_folder.as_posix(), exist_ok=True)
    print(
        "Folder for unprocessed logfiles is created at: {}".format(
            unprocessed_folder.as_posix()
        )
    )
    os.makedirs(processed_folder.as_posix(), exist_ok=True)
    print(
        "Folder for processed logfiles is created at: {}".format(
            processed_folder.as_posix()
        )
    )
    os.makedirs(db_folder.as_posix(), exist_ok=True)
    print("Folder for db export is created at: {}".format(db_folder.as_posix()))
    os.makedirs(csv_folder.as_posix(), exist_ok=True)
    print(
        "Folder for csv export is created at: {}".format(csv_folder.as_posix())
    )
    os.makedirs(model_folder.as_posix(), exist_ok=True)
    print(
        "Folder for model export is created at: {}".format(
            model_folder.as_posix()
        )
    )
    os.makedirs(statistics_folder.as_posix(), exist_ok=True)
    print(
        "Folder for statistics export is created at: {}".format(
            export_folder.as_posix()
        )
    )
