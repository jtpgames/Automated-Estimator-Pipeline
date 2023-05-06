# Automated Estimator Pipeline
This application can be used to automate the training and evaluation process of regression models. 
The main purpose is to train regression models that predict the response time of requests based on various factors 
like the request type and the number of parallel requests. The training and evaluation process takes advantage of 
automatic hyperparameter tuning for the regressor models and preprocessing steps.

# Setup
* clone the repository
* run ```cd <the_directory_you_cloned_the_repository>```
* create a python virtual environment in a directory called venv, e.g., python3 -m venv venv 
* activate virtual environment with 
  * Windows ```\<path_to_venv>\Scripts\activate```
  * unix ```source <path_to_venv>\bin\activate```
* run pip install -r requirements.txt
* add the root folder to the PYTHONPATH environment variable run ```export PYTHONPATH=${PYTHONPATH}:{logfile_analysis_root} ```
* run ```cd src``` in the repository folder
* run ```python setup.py``` to set up the folder structure


A configuration file for your environment is created under ```./resources/config/config.json```. This config file is used for the execution of all commands. Sample config files with different configurations are stored in the same folder.

# Pipeline
The pipeline has to main jobs. The first job is the extract transform load process for logfiles. It first reads all logfiles in the unprocessed logfile folder. 
The application need the logfiles to be in a format where each line represents the entrance or the exit of request. 
And each line should be in the following format.

```[THREAD_ID]	TIMESTAMP	[CMD-START|CMD-END]	CMD_TYPE```
eg.

```[2964349265]	2023-01-22 11:14:30.917255	CMD-START	ID_index```

Logfiles that are not in this format have to be converted. After all logfiles are in the correct format the logfiles are merged together by day.
After that each merged logfile is processed and the relevant features of a request like the request type, the number of parallel computed requests and the response time are extracted and stored in a database. 
In the configuration file can the user adjust which features should be extracted.

The logfile pipeline can be run with one of the following commands. 

```python src/pipeline.py logfile```

```python src/pipeline.py logfile --skip-convert```

```python src/pipeline.py logfile --skip-convert --skip-merge```


The second job is the automated estimator training and evaluation. It utilized sklearn classes like Estimators, Pipeline and GridSearchCV 
to systematically train models based on different estimators and tests different hyperparameter combinations. 
The best evaluated model will be exported in the end.

The estimator pipeline can be run with the following command

```python src/pipeline.py estimator```

It is also possible to run the whole pipeline with

```python src/pipeline.py run```

more information via ```python src/pipeline.py --help```

# Experiment
To test the automated estimator pipeline with a logfile that was generated with the load testing tool locust https://locust.io and the application TeaStore https://github.com/DescartesResearch/TeaStore follow these steps:
1. copy the logfile from the test_data folder to the folder resources/logfiles/unprocessed
2. run ```python src/pipeline.py run``` to execute the etl pipeline first and then automatically execute the estimator pipeline

Results will be the created database in resources/export/db and the best evaluated model in resources/models.

# Configuration
The configuration of the automated estimator pipeline is done via the config <root>/resources/config/config.json. 
The file consists of parts for each internal component of the application. To instance objects based on the given configuration the factory pattern is used.
The factories are located in src/factory/factories.py. To extend the functionality of the automated estimator pipeline the user has to create a class that 
inherits from the respective abstract base class and define a key under which the class has to be registered in the respective factory.

All keys in the factory.py can be used to set specific estimators or preprocessing steps in the configuration file.
Possible constructor parameters for estimators or preprocessing steps have to be look up in the scikit-learn documentation.

eg. DecisionTreeRegressor -> https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html
possible parameter for the hyperparameter tuning with GridSearchCV:
- criterion
- splitter
- max_depth
- min_samples_split
- min_samples_leaf
- min_weight_fraction_leaf
- max_features
- random_state
- max_leaf_nodes
- min_impurity_decrease
- ccp_alpha

In the following section the important configuration items will be explained

## Database
```json
  "database": {
    "row_limit": -1,
    "name": "NEWEST",
    "folder": ".../automated-estimator-pipeline/resources/export/db"
  }
```

* __row_limit__: specifies the max number of rows that are loaded from the database to perform the model training
* __name__: specifies the name of the Database that is used to save or load request data. With NEWEST, always the newest created database will be used
* __folder__: the database folder

## Outlier Detection
```json
  "outlier_detection": {
    "remove_outlier": true,
    "outlier_modus": "CMD",
    "std_threshold": 3
  },
```
* __remove_outlier__: specifies if outliers should be removed before the training process
* __outlier_modus__: specifies how the outliers should be removed, CMD - response time grouped by request type, ALL - response time over all requests 
* __std_threshold__: if a value is a certain number of standard deviations away from the mean, that data point is identified as an outlier and will be removed. Specifies the number of standard deviations

## Estimator Pipeline
```json
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
          "steps": [
            {
              "step": "std",
              "action": "std",
              "params": {}
            }
          ]
        }
      ],
      "estimators": [
        {
          "name": "LR",
          "params": {}
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
        "shuffle": true,
        "random_state": 42
      },
      "export_folder": "/Users/adrianliermann/IdeaProjects/automated-estimator-pipeline/resources/export/models"
    }
```
* __features__: the features that are used in the training of the regression models. Includes dependent and independent variables. All possible features are listed in the class DatabaseFeatureExtractorFactory. 
* __y_column__: the feature that represents the dependent variable
* __pipelines__: specifies which pipelines should be tested. If only one pipeline is specified the pipeline will be used for all estimators
* __steps__: specifies the preprocessing steps the pipeline should have. All possible pipeline steps are listed in class EstimatorPipelineActionFactory. The params can be used to specify an array of constructor parameters of the corresponding sklearn class that should be used in the hyperparameter tuning
* __estimators__: specifies the estimators that should be used in the training process. All possible estimators are listed in the class EstimatorFactory. The params can be used to specify an array of constructor parameters of the corresponding sklearn class that should be used in the hyperparameter tuning
* __export_folder__: the folder to store the resulting models

All other parameters are constructor parameters of the scikit learn classes GridSearchCV and KFold that can also be modified in the config.json

## Logfile ETL Pipeline
```json
  "logfile_etl_pipe": {
    "unprocessed_logfiles_folder": "/Users/adrianliermann/IdeaProjects/automated-estimator-pipeline/resources/logfiles/unprocessed",
    "processed_logfiles_folder": "/Users/adrianliermann/IdeaProjects/automated-estimator-pipeline/resources/logfiles/processed",
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
    "force": true,
    "converter": [
      "ARS",
      "WS",
      "LOCUST"
    ]
  },
```
* __unprocessed_logfiles_folder__: folder where the initial logfiles are expected. Logfiles have to follow a naming convention name_date.log. The date format is as follows YYYY-MM-DD
* __processed_logfiles_folder__: folder where the converted and by day merged logfiles are stored
* __converter__: the logfile converters that should be used. All possible converters are listed in the class ConverterFactory. Converters run if the name of a logfile matches with the pattern, that is specified in the converter. 
