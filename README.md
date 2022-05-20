# Structure
The project contains two packages. One package to execute an etl process for logfiles and one package to create machine learning models based on the extracted features
## logfile_etl
The configuration for the etl process is done via the json file ```resources/configuration/etl_config.json```. The following is an example for possible configurations. 
```
{
   "unprocessed_logfiles": "C:/Users/user/IdeaProjects/LogFileETL/resources/logfiles/unprocessed/",
   "processed_logfiles": "C:/Users/user/IdeaProjects/LogFileETL/resources/logfiles/processed/",
   "export_methods": ["db", "csv"],
   "db": {
      "folder": "C:/Users/user/IdeaProjects/LogFileETL/resources/export/db/"
   },
   "csv": {
      "folder": "C:/Users/user/IdeaProjects/LogFileETL/resources/export/csv/"
   },
   "extractors": [
      "Timestamp", "PR 1", "PR 2", "PR 3", "cmd", "response time", "First Command Start", "First Command Finished"
   ],
   "force": "True"
}
```
To run the process call ```python logfile_etl.py```


## regression_analysis
The configuration for the analysis is done via the json file ```resources/configuration/analysis_config.json```. The following is an example for possible configurations.
```
{
  "db": "C:/Users/lierm/IdeaProjects/LogFileETL/resources/export/db/trainingdata_2022-05-15.db",
  "features":  ["PR 1", "PR 3", "cmd", "First Command Start", "First Command Finished", "response time"],
  "y": "response time",
  "models": ["LR", "Ridge", "Lasso", "ElasticNet","SGD", "MLP", "KNN", "AdaLR", "AdaDT", "DT"]
}
```
To run the process call ```python regression_analysis.py```