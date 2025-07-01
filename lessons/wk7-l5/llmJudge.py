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

# Define the LLM-as-a-judge metric for TLDR
llm_judge_metric = GEval(
    name="LLM Judge TLDR Quality",
    criteria="Does the generated TLDR accurately and concisely summarize the main points of the publication as expressed in the reference TLDR?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)

judge_scores = []
judge_passed = []
judge_reasons = []

for idx, row in df.iterrows():
    print(f"Evaluating row {idx+1}/{len(df)}...")
    if pd.isna(row["tldr_generated"]) or pd.isna(row["tldr_truth"]):
        judge_scores.append(None)
        judge_passed.append(None)
        judge_reasons.append(None)
        print("  Skipped (missing TLDR data)")
    else:
        test_case = LLMTestCase(
            input=row["title_truth"],  # Optionally use title as context
            actual_output=row["tldr_generated"],
            expected_output=row["tldr_truth"]
        )
        eval_result = evaluate(test_cases=[test_case], metrics=[llm_judge_metric])
        try:
            test_result = eval_result.test_results[0]
            metric_data = test_result.metrics_data[0]
            score = metric_data.score
            passed = metric_data.success
            reason = metric_data.reason
        except Exception as e:
            score = None
            passed = None
            reason = str(e)
        judge_scores.append(score)
        judge_passed.append(passed)
        judge_reasons.append(reason)
        print(f"  LLM Judge Score: {score}, Passed: {passed}")

df_results = df.copy()
df_results["llm_judge_tldr_score"] = judge_scores
df_results["llm_judge_tldr_passed"] = judge_passed
df_results["llm_judge_tldr_reason"] = judge_reasons

# Remove any unnamed columns before saving
df_results = df_results.loc[:, ~df_results.columns.str.startswith('Unnamed')]

output_csv = "result/llm_judge_tldr_results.csv"
df_results.to_csv(output_csv, index=False)
print(f"\nEvaluation results saved to {output_csv}")
