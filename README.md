# Setup

The path of the src folder has to be on the PYTHONPATH environment variable. To add folder to the
run ```export PYTHONPATH=${PYTHONPATH}:{src_folder}} ```

# Structure

The project contains two packages. One package to execute an etl process for logfiles and one package to create machine
learning models based on the extracted features

## logfile_etl

The configuration for the etl process is done via the json file ```resources/configuration/etl_config.json```. The
following is an example for possible configurations.

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

**unprocessed_logfiles**:
Expects the folder of unprocessed logfiles. The function ```does_applies_for_file()``` of all registered
LogfileConverter is called for each logfile. If a LogfileConverter does apply for a file, the
method ```convert_logfile()``` is called and the converted files is stored in folder specified in processed_logfiles. A
new LogfileConverter has to inherit from AbstractLogfileConverter and has to be registered in the
class ```LogfileConverter```

**processed_logfiles**
Defines where all processed logfiles should be stored. All logfiles in this folder should be in a format where each line
is incoming request log or a responded requesat log.
Example ```[03340] 2021-12-31 00:00:02.158	INFO {n.n.}: <CMD-START>:<SDATA 0x5|ID_REQ_LCMD_MONGETMASTERSTATUS 0x21>```

All logfiles not complying for a LogfileConverter are automatically copied to the unprocessed_logfiles folder. After
that will all logfiles for the same day are merged into one file.

**export_methods**
Expects a list of export methods. Possible values are ```db``` and ```csv```.

**db**
Expects the path where the exported database should be stored

**csv**
Expects the path where the exported csv files should be stored

**extractors**
Expects a list of feature extractors. A feature extractor has to inherit from AbstractFeatureExtractor and has to be
registered in the class ```FeatureExtractor```. Possible values
are ```"Timestamp", "PR 1", "PR 2", "PR 3", "cmd", "response time", "First Command Start", "First Command Finished"```

**force**
Expects a boolean value that specifies if each request, that does not have a start or an end line, should be waiting on
a user input.

---
To run the process call ```python logfile_etl.py``` or ```python logfile_etl.py --help```

## regression_analysis

The configuration for the analysis is done via the json file ```resources/configuration/analysis_config.json```. The
following is an example for possible configurations.

```
{
  "db": "C:/Users/lierm/IdeaProjects/LogFileETL/resources/export/db/trainingdata_2022-05-15.db",
  "features":  ["PR 1", "PR 3", "cmd", "First Command Start", "First Command Finished", "response time"],
  "y": "response time",
  "models": ["LR", "Ridge", "Lasso", "ElasticNet","SGD", "MLP", "KNN", "AdaLR", "AdaDT", "DT"]
}
```

**db**
Expects the path of a database with stored logfile information.

**features**
Expects a list of feature extractors. A feature extractor has to inherit from AbstractFeatureExtractor and has to be
registered in the file ```feature_extractors.py```. It loads information from the database and creates a Dataframe that
can be used to train models on. Possible values
are ```"PR 1", "PR 3", "cmd", "First Command Start", "First Command Finished", "response time"```

**y**
Expects the name of the feature, that should be predicted

**models**
Expects a list of models, that should be trained on the extracted features. Possible values
are ```"LR", "Ridge", "Lasso", "ElasticNet","SGD", "MLP", "KNN", "AdaLR", "AdaDT", "DT"```



---
To run the process call ```python regression_analysis.py```