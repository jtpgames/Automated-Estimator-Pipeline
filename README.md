# Setup
* clone the repository
* run ```cd <the_directory_you_cloned_the_repository>```
* create a python virtual environment in a directory called venv, e.g., python3 -m venv venv 
* activate virtual environment with 
  * Windows ```\<path_to_venv>\Scripts\activate```
  * unix ```source <path_to_venv>\bin\activate```
* run pip install -r requirements.txt
* add the root folder to the PYTHONPATH environment variable run ```export PYTHONPATH=${PYTHONPATH}:{logfile_analysis_root} ```
* run ```./src/setup.py``` in the src folder to set up the resource folder structure


A configuration file for your environment is created under ```./resources/config/config.json```. This config file is used for the execution of all commands. Sample config files with different confiugrations are stored in the same folder.

# Pipeline
This repository has the main purpose of automating the training and evaluation process of regression models. 

# Experiment

Before you can run the pipeline you have to put the Logfiles of the production system in the folder /resources/logfiles/unprocessed. 
Ask Juri Tomak for production logfiles of gs electronic.

```python src/pipeline.py run```

To run only the logfile pipeline
```python src/pipeline.py logfile```

To run only the estimator pipeline
```python src/pipeline.py estimator```

more information via ```python src/pipeline.py --help```

# Extended Configurations
All keys in the factory.py can be used to set specific estimators or preprocessing steps in the configuration file. 
Possible constructor parameters for estimators or preprocessing steps have to be look up in the scikit-learn documentation.

eg. DecisionTreeRegressor -> https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html 
possible parameter for gridsearch:
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

