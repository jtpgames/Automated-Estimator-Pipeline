import logging
import os

import typer

from src.analysis.estimator_pipeline import EstimatorPipeline
from src.configuration import Configuration
from src.logfile_etl.logfile_etl_pipeline import LogfileETLPipeline
from src.workload_characterization import WorkloadCharacterization

# needed to get reproducible hash values for objects
os.environ["PYTHONHASHSEED"] = "0"

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)

app = typer.Typer()

config: Configuration = None


@app.command()
def run(skip_convert: bool = typer.Option(False, help="skips the logfile convert phase in the logfile etl process"),
        skip_merge: bool = typer.Option(False, help="skips the logfile merge process in the logfile etl process")):
    logfile(skip_convert, skip_merge)
    estimator()
    #workload()


@app.command()
def logfile(skip_convert: bool = typer.Option(False, help="skips the logfile convert phase in the logfile etl process"),
            skip_merge: bool = typer.Option(False, help="skips the logfile merge process in the logfile etl process")):
    skip_stages = {"converter": skip_convert, "merger": skip_merge}
    logfile_etl = LogfileETLPipeline(config, skip_stages)
    logfile_etl.run()


@app.command()
def estimator():
    estimator_pipeline = EstimatorPipeline(config)
    estimator_pipeline.run()


@app.command()
def workload():
    workload_characterization = WorkloadCharacterization(config)
    workload_characterization.run()


# TODO is also executed when calling --help on subcommand or on error
@app.callback()
def callback(config_file: str = "resources/config/gs_without_sel_dt.json"):
    global config

    config = Configuration(config_file)
    config.load()


if __name__ == "__main__":
    app()
