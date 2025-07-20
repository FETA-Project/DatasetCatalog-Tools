# LLM Analyzer
This tools is used for research paper summarization for dataset quality analysis. 

The output of this tool is a dataset report file mainly used for [Dataset Catalog](https://dataset-catalog.liberouter.org/).

# Installation 
Clone this repo and go to the directory
* cd DatasetCatalog-Tools/llm-analysis

Create virtual environemnt
* python3 -m venv venv
* . ./venv/bin/activate 

Install required python modules
* pip3 install -r requirements.txt

Run example
* cd src
* python3 main.py

If everything runs without any issue you are ready for configuration 

## Configuration
Edit mainly conf/basic_config.toml where is specification of input, output and debug files.
