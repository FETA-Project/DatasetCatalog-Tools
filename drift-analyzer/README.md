# Drift Analyzer
This tools provides dataset stability analysis that is based on drift detection method Model-based Feature Weight Drift Detection (MFWDD). The dataset stability is evaluated based on worflow used in "experiment_runner.py". The analysis is segmented in these catagories: 
* Global: Full dataset drift detection regardless label column
* Per Class: Per class drift detection (requires fully labeled dataset)
* Per Feature: Impact analysis of specific features to the drift

The output of this tool is a dataset report file used for [Dataset Catalog](https://dataset-catalog.liberouter.org/). Additionally, it provides additional metadata that can be further analysed. An example is available using a Jupyter notebook in the "resources" directory.

# Installation 
Clone this repo and go to the directory
* cd DatasetCatalog-Tools/drift-analysis

Create virtual environemnt
* python3 -m venv venv
* . ./venv/bin/activate 

Run the evaluation
* python3 experiment_runner.py

If everything runs without any issue you are ready for configuration 

## Configuration
Edit mainly experiment_runner.py where specification of experiment parameters can be defined. The main lines that requires modification are commented by "Action" keyword.  
