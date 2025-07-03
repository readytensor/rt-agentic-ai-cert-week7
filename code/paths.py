"""Path configurations for the project."""

import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.join(PROJECT_ROOT, "code")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
METRICS_DIR = os.path.join(CODE_DIR, "metrics")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

# Data files
GOLDEN_DATASET_CSV = os.path.join(DATA_DIR, "golden_dataset.csv")
GOLDEN_DATASET_JSON = os.path.join(DATA_DIR, "golden_dataset.json")
TEST_SET_CSV = os.path.join(DATA_DIR, "test_set.csv")
EVALUATION_RESULTS_CSV = os.path.join(OUTPUTS_DIR, "evaluation_results.csv")
COMPLETE_EVALUATION_RESULTS_CSV = os.path.join(
    OUTPUTS_DIR, "complete_evaluation_results.csv"
)
