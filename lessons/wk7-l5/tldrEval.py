import os
from dotenv import load_dotenv
import pandas as pd
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval import evaluate

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found in environment. Please add it to your .env file.")
    exit(1)

csv_path = "dataset/golden_dataset.csv"
df = pd.read_csv(csv_path)
df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

similarity_metric = GEval(
    name="TLDR Similarity",
    criteria="Does the generated TLDR convey the same meaning as the reference TLDR?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)
faithfulness_metric = GEval(
    name="TLDR Faithfulness",
    criteria="Is the generated TLDR factually consistent with the reference TLDR, without introducing hallucinated or incorrect information?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)

tldr_similarity_scores = []
tldr_similarity_passed = []
tldr_similarity_reasons = []
tldr_faithfulness_scores = []
tldr_faithfulness_passed = []
tldr_faithfulness_reasons = []

for idx, row in df.iterrows():
    print(f"Evaluating row {idx+1}/{len(df)}...")
    if pd.isna(row["tldr_generated"]) or pd.isna(row["tldr_truth"]):
        tldr_similarity_scores.append(None)
        tldr_similarity_passed.append(None)
        tldr_similarity_reasons.append(None)
        tldr_faithfulness_scores.append(None)
        tldr_faithfulness_passed.append(None)
        tldr_faithfulness_reasons.append(None)
        print("  Skipped (missing TLDR data)")
    else:
        test_case = LLMTestCase(
            input=row["title_truth"],
            actual_output=row["tldr_generated"],
            expected_output=row["tldr_truth"]
        )
        sim_result = evaluate(test_cases=[test_case], metrics=[similarity_metric])
        try:
            sim_test_result = sim_result.test_results[0]
            sim_metric_data = sim_test_result.metrics_data[0]
            sim_score = sim_metric_data.score
            sim_passed = sim_metric_data.success
            sim_reason = sim_metric_data.reason
        except Exception as e:
            sim_score = None
            sim_passed = None
            sim_reason = str(e)
        tldr_similarity_scores.append(sim_score)
        tldr_similarity_passed.append(sim_passed)
        tldr_similarity_reasons.append(sim_reason)

        faith_result = evaluate(test_cases=[test_case], metrics=[faithfulness_metric])
        try:
            faith_test_result = faith_result.test_results[0]
            faith_metric_data = faith_test_result.metrics_data[0]
            faith_score = faith_metric_data.score
            faith_passed = faith_metric_data.success
            faith_reason = faith_metric_data.reason
        except Exception as e:
            faith_score = None
            faith_passed = None
            faith_reason = str(e)
        tldr_faithfulness_scores.append(faith_score)
        tldr_faithfulness_passed.append(faith_passed)
        tldr_faithfulness_reasons.append(faith_reason)

        print(f"  Similarity Score: {sim_score}, Passed: {sim_passed}")
        print(f"  Faithfulness Score: {faith_score}, Passed: {faith_passed}")

df_results = df.copy()
df_results["tldr_similarity_score"] = tldr_similarity_scores
df_results["tldr_similarity_passed"] = tldr_similarity_passed
df_results["tldr_similarity_reason"] = tldr_similarity_reasons
df_results["tldr_faithfulness_score"] = tldr_faithfulness_scores
df_results["tldr_faithfulness_passed"] = tldr_faithfulness_passed
df_results["tldr_faithfulness_reason"] = tldr_faithfulness_reasons

df_results = df_results.loc[:, ~df_results.columns.str.startswith('Unnamed')]

output_csv = "result/tldr_similarity_faithfulness_results.csv"
df_results.to_csv(output_csv, index=False)
print(f"\nEvaluation results saved to {output_csv}")
