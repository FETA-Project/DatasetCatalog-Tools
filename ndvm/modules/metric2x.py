"""
Final, robust, and optimized version of the Dataset Label Association Calculation.
This version uses joblib for stable parallel processing and sets environment 
variables to prevent library-induced deadlocks, ensuring the evaluation does not hang.
"""
import os
import pickle
import sys

# --- CRITICAL FIX: Set environment variables BEFORE importing numpy/sklearn ---
# This prevents libraries from creating their own nested thread pools, which causes deadlocks.
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import auc
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from tqdm import tqdm

# --- MODIFIED: Using joblib for more robust parallel processing ---
from joblib import Parallel, delayed

from core import AbstractMetric


# --- MODIFIED: The worker function is simplified for joblib ---
def _evaluate_permutation_task(X_data, y_permuted, y_original, classifiers):
    """Worker function for a single permutation evaluation."""
    cv_strategy = StratifiedKFold(n_splits=2, shuffle=True, random_state=None)
    
    permuted_scores = [
        cross_val_score(clf, X_data, y_permuted, cv=cv_strategy, scoring="f1_macro").mean()
        for clf in classifiers.values()
    ]
    
    correlation = np.corrcoef(y_permuted, y_original)[0, 1]
    
    return np.array(permuted_scores), correlation

class Association(AbstractMetric):
    def __init__(self, dataset, label, multiclass=False, verbose=0, n_permutations=100, cores=None):
        self.raw_dataset = dataset
        self.label_column = label
        self.is_multiclass = multiclass
        self.verbose = verbose
        self.n_permutations = n_permutations
        # Use joblib's convention for all cores: -1
        self.cores = cores if cores is not None else -1 
        self.classifiers_to_use = ["DT", "RF", "XGB"]
        self.permutation_percentages = [50, 30, 10, 1]
        self.cv_folds = 2
        self.X_scaled, self.y = None, None
        self.classifiers, self.initial_scores = {}, None
        self.permuted_scores, self.correlations = None, None
        self.p_values, self.slopes, self.auc_scores = None, None, None
        self.final_result = {}

    def run_evaluation(self):
        self._load_and_prepare_data()
        self._setup_classifiers()
        self._run_initial_evaluation()
        self._run_permutation_tests()
        self._analyze_results()
        if self.verbose >= 1: self.print_results()
        return self.get_score()

    def get_details(self, output_dir_metadata_base):
        output_dir = f"{output_dir_metadata_base}-metric2"
        try:
            os.makedirs(output_dir, exist_ok=True)
            temp_data = {'raw_dataset': self.raw_dataset, 'X_scaled': self.X_scaled, 'y': self.y}
            self.raw_dataset, self.X_scaled, self.y = None, None, None
            file_path = os.path.join(output_dir, "metric2x.obj")
            with open(file_path, "wb") as f:
                pickle.dump(self, f)
            if self.verbose >= 1: print(f"Association metric object saved to: {file_path}")
            self.raw_dataset, self.X_scaled, self.y = temp_data['raw_dataset'], temp_data['X_scaled'], temp_data['y']
        except Exception as e:
            print(f"Error saving metric details to {output_dir}: {e}", file=sys.stderr)

    def get_name(self):
        return "Association"

    def _load_and_prepare_data(self):
        if self.verbose >= 1: print("Loading and preparing data...")
        try:
            self.y = pd.Series(self.raw_dataset[self.label_column].astype('category').cat.codes)
            X_raw = self.raw_dataset.drop(columns=[self.label_column])
            self.X_scaled = MinMaxScaler().fit_transform(X_raw)
        except Exception as e:
            print(f"Error during data preparation: {e}", file=sys.stderr)
            sys.exit(1)

    def _setup_classifiers(self):
        if self.verbose >= 1: print("Setting up classifiers...")
        clfs_pool = {
            "DT": DecisionTreeClassifier(),
            "RF": RandomForestClassifier(),
            "XGB": XGBClassifier(eval_metric="logloss" if not self.is_multiclass else "mlogloss"),
        }
        self.classifiers = {name: clfs_pool[name] for name in self.classifiers_to_use}

    def _run_initial_evaluation(self):
        if self.verbose >= 1: print("Running initial evaluation on original data...")
        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=42)
        scores = [cross_val_score(clf, self.X_scaled, self.y, cv=cv, scoring="f1_macro").mean() for clf in self.classifiers.values()]
        self.initial_scores = np.array(scores).reshape(1, -1)

    def _create_permuted_label(self, percentage):
        y_permuted = self.y.copy()
        indices_to_permute = []
        for class_label in self.y.unique():
            class_indices = self.y[self.y == class_label].index
            num_to_permute = round(len(class_indices) * percentage / 100)
            if num_to_permute > 0:
                indices_to_permute.extend(np.random.choice(class_indices, num_to_permute, replace=False))
        if not indices_to_permute: return y_permuted
        permuted_subset = np.random.permutation(indices_to_permute)
        y_permuted.iloc[indices_to_permute] = self.y.iloc[permuted_subset].values
        if np.array_equal(self.y.values, y_permuted.values):
            return self._create_permuted_label(percentage)
        return y_permuted

    # --- MODIFIED: Switched to joblib for stable parallel execution ---
    def _run_permutation_tests(self):
        """Performs permutation testing using the robust joblib library."""
        num_tasks = self.n_permutations * len(self.permutation_percentages)
        if self.verbose >= 1: 
            print(f"Running {num_tasks} permutation tests using {self.cores} cores...")
        
        # Create a generator for tasks to save memory
        tasks = (
            (self.X_scaled, self._create_permuted_label(p), self.y, self.classifiers)
            for _ in range(self.n_permutations)
            for p in self.permutation_percentages
        )

        # Use joblib's Parallel to run tasks, which integrates with tqdm
        results = Parallel(n_jobs=self.cores)(
            delayed(_evaluate_permutation_task)(*task) 
            for task in tqdm(tasks, total=num_tasks, desc="Evaluating Permutations")
        )
        
        # Reshape the flat list of results into the required 3D/2D arrays
        num_clfs, num_percs = len(self.classifiers), len(self.permutation_percentages)
        self.permuted_scores = np.zeros((self.n_permutations, num_percs, num_clfs))
        self.correlations = np.zeros((self.n_permutations, num_percs))
        
        for i, (scores, corr) in enumerate(results):
            perm_idx = i // num_percs
            perc_idx = i % num_percs
            self.permuted_scores[perm_idx, perc_idx, :] = scores
            self.correlations[perm_idx, perc_idx] = corr
    
    def _analyze_results(self):
        if self.verbose >= 1: print("Analyzing results...")
        num_clfs, num_percs = len(self.classifiers), len(self.permutation_percentages)
        self.p_values = np.zeros((num_clfs, num_percs))
        for clf_idx in range(num_clfs):
            for perc_idx in range(num_percs):
                count = np.sum(self.permuted_scores[:, perc_idx, clf_idx] >= self.initial_scores[0, clf_idx])
                self.p_values[clf_idx, perc_idx] = (count + 1) / (self.n_permutations + 1)

        self.slopes, self.auc_scores = {}, {}
        mean_correlations = self.correlations.mean(axis=0)
        for i, name in enumerate(self.classifiers.keys()):
            mean_permuted_scores = self.permuted_scores[:, :, i].mean(axis=0)
            self.slopes[name], _ = np.polyfit(mean_correlations, mean_permuted_scores, 1)
            self.auc_scores[name] = auc(mean_correlations, mean_permuted_scores)
            
        max_scores_per_perm = np.max(self.permuted_scores.mean(axis=0), axis=1)
        max_score_at_1_percent = max_scores_per_perm[-1] if len(max_scores_per_perm) > 0 else 0
        auc_of_max_curve = auc(mean_correlations, max_scores_per_perm)
        
        self.final_result["Association"] = (0.5 - auc_of_max_curve / max_score_at_1_percent) / 0.25 if max_score_at_1_percent > 1e-6 else 0.0
        self.final_result["Max Clf Score"] = max_score_at_1_percent
        self.final_result["Raw Slope"] = f"{max(self.slopes.values()):.4f} ({max(self.slopes, key=self.slopes.get)})" if self.slopes else "N/A"
        self.final_result["Raw AUC"] = f"{max(self.auc_scores.values()):.4f} ({max(self.auc_scores, key=self.auc_scores.get)})" if self.auc_scores else "N/A"

    def get_p_value_status(self):
        pv_df = pd.DataFrame(self.p_values, index=self.classifiers.keys(), columns=self.permutation_percentages)
        max_initial_score = self.initial_scores.max()
        for clf_idx, clf_name in enumerate(self.classifiers.keys()):
            if np.sum(pv_df.loc[clf_name] <= 0.01) == len(self.permutation_percentages):
                return "Good" 
            if np.sum(pv_df.loc[clf_name] <= 0.01) > 0:
                return "Mid"
        return "Bad"

    def get_score(self):
        if self.p_values is None: self._analyze_results()
        pv_df = pd.DataFrame(self.p_values, index=self.classifiers.keys(), columns=self.permutation_percentages)
        self.final_result["P-value status"] = self.get_p_value_status()
        self.final_result["P-value table"] = str(pv_df)
        return self.final_result

    def print_results(self):
        print("\n" + "="*20 + " RESULTS " + "="*20)
        pv_df = pd.DataFrame(self.p_values, index=self.classifiers.keys(), columns=self.permutation_percentages)
        print("P-value Table:")
        print(pv_df)
        print("\nClassifier Slopes:")
        for name, slope in self.slopes.items(): print(f"  {name}: {slope:.4f}")
        print("\nFinal Score Summary:")
        for key, value in self.final_result.items():
            if key != "P-value table": print(f"  {key}: {value}")
        print("="*49)
