import json
import pathlib
from datetime import datetime

if __name__ == "__main__":
    parent_dir = pathlib.Path().absolute().parent
    resource_folder = parent_dir / "resources"
    unprocessed_folder = resource_folder / "unprocessed"
    processed_folder = resource_folder / "processed"
    db_folder = resource_folder / "export" / "db"
    csv_folder = resource_folder / "export" / "csv"
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
        "features": ["PR 1", "PR 3", "cmd", "First Command Start",
                     "First Command Finished", "response time"],
        "y": "response time",
        "models": ["LR", "Ridge", "Lasso", "ElasticNet", "SGD", "MLP", "KNN",
                   "AdaLR", "AdaDT", "DT"],
        "model_save_path": model_folder.as_posix()
    }

    analysis_config_file_path = resource_folder / "config" / "analysis_config.json"
    etl_config_file_path = resource_folder / "config" / "etl_config.json"

    with open(analysis_config_file_path, 'w') as fp:
        json.dump(analysis_config, fp)

    with open(etl_config_file_path, 'w') as fp:
        json.dump(etl_config, fp)
