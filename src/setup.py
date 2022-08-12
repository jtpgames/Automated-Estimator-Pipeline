import json
import pathlib
from datetime import datetime
import os

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

    etl_config = {
        "unprocessed_logfiles": unprocessed_folder.as_posix(),
        "processed_logfiles": processed_folder.as_posix(),
        "export_methods": ["db", "csv"],
        "db": {
            "folder": db_folder.as_posix()
        },
        "csv": {
            "folder": csv_folder.as_posix()
        },
        "extractors": [
            "Timestamp", "PR 1", "PR 2", "PR 3", "cmd", "response time",
            "First Command Start", "First Command Finished",
            "List parallel requests start", "List parallel requests finished"
        ],
        "force": "True"
    }

    analysis_config = {
        "db": db_file.as_posix(),
        "db_limit": -1,
        "features": ["PR 1", "PR 3", "cmd", "First Command Start",
                     "First Command Finished", "response time"],
        "y": "response time",
        "models": ["LR", "Ridge", "Lasso", "ElasticNet", "SGD", "MLP", "KNN",
                   "AdaLR", "AdaDT", "DT"],
        "model_save_path": model_folder.as_posix()
    }

    characterization_config = {
        "db": db_file.as_posix(),
        "db_limit": -1,
        "export_folder": statistics_folder.as_posix()
    }
    configuration_folder = resource_folder / "config"

    analysis_config_file_path = configuration_folder / "analysis_config.json"
    etl_config_file_path = configuration_folder / "etl_config.json"
    characterization_config_file_path = configuration_folder / "characterization_config.json"

    os.makedirs(configuration_folder.as_posix(), exist_ok=True)


    with open(analysis_config_file_path, 'w+') as fp:
        json.dump(analysis_config, fp)

    with open(etl_config_file_path, 'w+') as fp:
        json.dump(etl_config, fp)

    with open(etl_config_file_path, 'w+') as fp:
        json.dump(characterization_config, fp)

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
    os.makedirs(export_folder.as_posix(), exist_ok=True)
    print(
        "Folder for statistics export is created at: {}".format(
            export_folder.as_posix()
        )
    )
