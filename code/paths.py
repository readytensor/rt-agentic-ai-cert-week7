"""Path configurations for the project."""

import os


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CODE_DIR = os.path.join(ROOT_DIR, "code")

DATA_DIR = os.path.join(ROOT_DIR, "data")

METRICS_DIR = os.path.join(CODE_DIR, "metrics")

OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")

CONFIG_DIR = os.path.join(ROOT_DIR, "config")

CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config.yaml")

# Data files
GOLDEN_DATASET_CSV = os.path.join(DATA_DIR, "golden_dataset.csv")

GOLDEN_DATASET_JSON = os.path.join(DATA_DIR, "golden_dataset.json")


EVALUATION_RESULTS_CSV = os.path.join(OUTPUTS_DIR, "evaluation_results.csv")

COMPLETE_EVALUATION_RESULTS_CSV = os.path.join(
    OUTPUTS_DIR, "complete_evaluation_results.csv"
)
