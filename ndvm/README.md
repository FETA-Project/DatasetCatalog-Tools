# NDVM (Network Dataset Evaluation Metrics)

The Network Dataset Evaluation report is a tool used to analyze datasets to estimate trustworthiness. The provided solution can describe basic parameters such as the number of classes, imbalance ratio, and duplicated samples. There are also additional modules to provide more advanced evaluation:

* Dataset Redundancy
This metric is focused on the level of dataset size redundancy. Using this measure, one can estimate what portion of the original dataset can be randomly removed while keeping the classification performance drop below a certain controlled level. Zero redundancy indicates that there is not enough data for the classification task. For evaluation, we use the pool of classifiers and acceptance level $\alpha$ to generally assess the level of redundancy with a certain probability. The metric domain is $[0, 1]$, and it describes the percentage size of the dataset that is redundant. 

* Dataset Association Quality
It evaluates the level of association between labels and respective data. Especially for the public datasets, we don't know how the dataset was collected, and if it's meaningful to apply an ML algorithm to such a dataset. The level of association is estimated based on permutation tests, which are interpreted by this novel metric. As a result, we get an estimate of how strong the connection is between data and related labels. The metric domain is $[0, 1]$ and it corresponds to the level of association between data and labels in the dataset.

* Dataset Class Similarity
The last metric looks at the dataset classes. We propose a method to estimate how instances of different classes are similar to each other. In other words, how complex the classification task generally is on the input dataset. The metric measures relative class similarity using autoencoders and their respective reconstruction error. Calculated relative similarity lays out direct indicators of how prone are other machine learning models to misclassifications. Since this metric represents average relative reconstruction error over all instances of non-base classes, the domain are positive numbers -- multiples of reconstruction error on base class. $M_3 <= 1$ means that the autoencoder performs similarly for all the classes and from this point of view, classes are similar, or even some classes might seem as a subset of the base class in the feature space. On the other hand, if $M_3 > 1 + K$, classes are different in the feature space and might be easier to separate from the base class.

The output of this tool is a dataset report file used for [Dataset Catalog](https://dataset-catalog.liberouter.org/). Additionally, it provides additional metadata that can be further analysed. An example is available using a Jupyter notebook in the resources directory.

# Installation 
Clone this repo and go to the directory
* cd DatasetCatalog-Tools/ndvm

Create virtual environemnt
* python3 -m venv venv
* . ./venv/bin/activate 

Install required python modules
* pip3 install -r requirements.txt

Run example
* python3 dataset_report.py

If everything runs without any issue you are ready for configuration of dataset evalution tool.

## Configuration
### config.py
The main configuration file is represented by a Python module. You can choose any name or location you want. The default name is "config.py," and it is located at the root of this repository. In this file, you can select (comment/uncomment) advanced metrics you would like to run. Also, there are additional parameters that globally affect the dataset evaluation. An explanation of each parameter is provided in the config.py file.

### Metric configuration
Each advanced metric selected in the main configuration file (section config.py above) is inherited from core.py, which defines the structure of each metric. This provides a unified interface for easier development. Each metric can have special parameters relevant just for the purposes of the metric. These parameters are part of class attributes in the metric module. Typically you can configure the pool of classifiers, number of repetitions, ... For further details, please check the comments in the metric module or read our papers with more detailed explanations and experiments. 
