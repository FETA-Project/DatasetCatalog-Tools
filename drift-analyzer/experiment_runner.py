import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cesnet_datazoo.datasets import CESNET_TLS_Year22
from cesnet_datazoo.config import DatasetConfig, AppSelection
from datetime import datetime, timedelta


from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import sklearn.metrics as metrics
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report,confusion_matrix,f1_score
from sklearn.model_selection import train_test_split
from copy import deepcopy

from scipy import stats
from joblib import dump, load

import warnings
warnings.filterwarnings('ignore') 

from detector.detector import DriftDetector, Config
from detector.logger import Logger
from detector.test import KSTest, WassersteinTest
from detector.analyser import LastWeekAnalyser
from detector.runner import ExperimentRunner, ExperimentConfig
from sklearn.preprocessing import LabelEncoder

DATE = False

label_encoder = LabelEncoder()
# Action: Change path to the input dataset
# df = pd.read_csv("#cesnet-miners22-ppi/miners-design.csv")
df = pd.read_csv("...")
# Action: Change label name to convert label string to numbers
# df["label"] = label_encoder.fit_transform(df["label"])

if DATE:
    df = df.sample(frac=1).reset_index(drop=True)
    df = df.reset_index()
    # Action: Change date identifier
    # df['date'] = pd.to_datetime(df['date'])
    df['...'] = pd.to_datetime(df['...'])
    # Action: Select columns with features
    # feat_names = df.columns[:-2]
    feat_names = ... 

    # Action: Validate experiment configuration variables (binar/mulitclass, label name, index name, experiment name). No need to change thresholds
    # Action 2: For the dataset report purpose, change the retrain flag from "False" to "True" to get results for both scenarios
    experiment_config = ExperimentConfig(
        data = df,
        chosen_features = feat_names,
        index_column = "date",
        window_length = timedelta(days=1),
        global_test = WassersteinTest(drift_threshold_global=0.04,drift_threshold_single = 0.1), 
        experiment_name = "Baseline",
        target_column = "APP",
        class_test = KSTest(drift_threshold_global=0.475,drift_threshold_single = 0.05), 
        analyser_test = None,
        use_time_index = True,
        chunk_length = 7,
        model = XGBClassifier(), #XGBClassifier(objective="multi:softmax"),
        retrain = False,
        training_window = 7
    )
else:
    df = df.sample(frac=1).reset_index(drop=True)
    df = df.reset_index()
    feat_names = df.columns.drop(['label', 'index'])

    experiment_config = ExperimentConfig(
        data = df,
        chosen_features = feat_names,
        index_column = "index",
        window_length = 10000,
        global_test = WassersteinTest(drift_threshold_global=0.04,drift_threshold_single = 0.1), 
        experiment_name = "Baseline",
        target_column = "label",
        class_test = KSTest(drift_threshold_global=0.475,drift_threshold_single = 0.05), 
        analyser_test = None,
        use_time_index = False,
        chunk_length = 7,
        model = XGBClassifier(), #XGBClassifier(objective="multi:softmax"),
        retrain = False,
        training_window = 7
    )

experimet_runner = ExperimentRunner([experiment_config])
logs = experimet_runner.run()

mapping = {int(i): label for i, label in enumerate(label_encoder.classes_)}
logs[0].set_label_names(mapping)

import pickle
# Action: Change name of the output file
# with open('logs_miners_retrained.pkl', 'wb') as outp:
with open('...', 'wb') as outp:
    pickle.dump(logs, outp, pickle.HIGHEST_PROTOCOL)

baseline_log = logs[0].get_logs()
from pprint import pprint 

def get_top_drifted_class(logger_data):
    tmp_data = logger_data["class_drift"].apply(ks_sample_drifted)
    tmp_max = []
    for c in tmp_data.columns:
        try:
            tmp_max.append({"class":c,"true_drift":tmp_data[c].value_counts()[True]})
        except Exception as e:
            tmp_max.append({"class":c,"true_drift": 0})
    return tmp_max

def get_top_drifted_feature(logger_data):
    tmp_data = logger_data["feature_drift"].apply(ws_feature_drifted)
    tmp_max = []
    for c in tmp_data.columns:
        try:
            tmp_max.append({"feature":c,"true_drift":tmp_data[c].value_counts()[True]})
        except Exception as e:
            tmp_max.append({"feature":c,"true_drift": 0})
    return tmp_max

# Action validate drift threshold with experiment config
ks_drift_threshold_single = 0.05
ks_drift_threshold_global = 0.475
ws_drift_threshold_single = 0.1
ws_drift_threshold_global = 0.04

def ws_feature_drifted(metric):
    return metric > ws_drift_threshold_single

def ws_sample_drifted(metric):
    return metric > ws_drift_threshold_global

def ks_sample_drifted(metric):
    return metric < ks_drift_threshold_global

def ks_feature_drifted(metric):
    return metric < ks_drift_threshold_single


# Celkovy pocet driftu
print("=== Drifts number ===")
print("Baseline Global", baseline_log["global_drift"]["is_drifted"].value_counts())
# top N drifted classes
print("=== Top 5 drifted classes ===")
print("Baseline Class")
top = get_top_drifted_class(baseline_log)
maxitem = sorted(top, key=lambda x:x["true_drift"],reverse=True)[:5]
pprint(maxitem)
# top N drifted features
print("=== Top 5 drifted features ===")
print("Baseline Feature")
top = get_top_drifted_feature(baseline_log)
maxitem = sorted(top, key=lambda x:x["true_drift"],reverse=True)[:5]
pprint(maxitem)

